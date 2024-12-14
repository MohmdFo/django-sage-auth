import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django.views import View
from sage_otp.helpers.choices import OTPState, ReasonOptions
from sage_otp.helpers.exceptions import InvalidTokenException, OTPExpiredException
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.models import SageUser
from sage_auth.utils import get_backends, send_email_otp
from sage_auth.signals import otp_expired, otp_failed, otp_verified

logger = logging.getLogger(__name__)


class VerifyOtpMixin(View):
    """
    Mixin for verifying OTPs in user authentication and reactivation flows.

    This mixin provides a secure, reusable structure for OTP verification
    in Django.
    views, supporting use cases like email or phone number activation
    and password recovery.
    It checks the validity of the OTP, manages failed attempts, and
    initiates account activation if the OTP is verified successfully
    """

    otp_manager = OTPManager()
    user_identifier = None
    lockout_duration = getattr(settings, "OTP_LOCKOUT_DURATION", 1)
    lock_user = getattr(settings, "OTP_MAX_REQUEST_TIMEOUT", 4)
    block_count = getattr(settings, "OTP_BLOCK_COUNT", 1)
    reason = ReasonOptions.EMAIL_ACTIVATION
    success_url = None
    minutes_left_expiry = None
    seconds_left_expiry = None
    reactivate_process = False

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is in the signup process by verifying the session key
        and ensure request setup before handling the request.
        """
        user = self.get_user_by_identifier()
        if user.is_block:
            messages.error(self.request, _("You have been blocked"))
            logger.warning("You have been blocked from accessing website")
            raise PermissionDenied("You have been blocked")
        if not self.reactivate_process:
            if not request.session.get("spa"):
                logger.warning("Unauthorized access attempt: no active signup session.")
                raise PermissionDenied("403 Forbidden")
        return super().dispatch(request, *args, **kwargs)

    def verify_otp(self, user_identifier, entered_otp):
        """Verify OTP and activate the user if it matches."""
        try:
            logger.debug("Verifying OTP for identifier: %s", user_identifier)
            user = self.get_user_by_identifier()
            otp_instance = self.otp_manager.get_otp(
                identifier=user.id, reason=self.reason
            )
            otp_max = getattr(settings, "OTP_MAX_FAILED_ATTEMPTS", 4)
            otp_expiry_time = otp_instance.last_sent_at + timedelta(
                seconds=self.otp_manager.EXPIRE_TIME.seconds
            )
            time_left_to_expire = (otp_expiry_time - tz.now()).total_seconds()

            if time_left_to_expire <= 0:
                otp_instance.update_state(OTPState.EXPIRED)
                otp_expired.send(sender=self.__class__, user=user, reason=self.reason)
                messages.error(
                    self.request,
                    _("Your OTP has expired. A new OTP has been sent."),
                )
                self.send_new_otp(user)
                return False

            if otp_instance.failed_attempts_count >= otp_max:
                otp_failed.send(
                    sender=self.__class__,
                    user=user,
                    reason=self.reason,
                    attempts=otp_instance.failed_attempts_count,
                )
                messages.error(
                    self.request,
                    _("Too many failed attempts. A new OTP has been sent."),
                )
                self.send_new_otp(user)
                return False

            if otp_instance.token == entered_otp:
                user.is_active = True
                otp_instance.state = OTPState.CONSUMED
                user.save()
                otp_instance.save()
                otp_verified.send(
                    sender=self.__class__, user=user, success=True, reason=self.reason
                )
                messages.success(
                    self.request, _("Your OTP was successfully verified.")
                )
                return user
            else:
                otp_instance.failed_attempts_count += 1
                otp_instance.save()
                otp_failed.send(
                    sender=self.__class__,
                    user=user,
                    reason=self.reason,
                    attempts=otp_instance.failed_attempts_count,
                )
                messages.error(self.request, _("The OTP entered is incorrect."))
                return False

        except Exception as e:
            logger.error("OTP verification error: %s", e)
            otp_failed.send(sender=self.__class__, user=None, reason=self.reason, attempts=0)
            return False

    def locked_user(self, count):
        return count >= self.lock_user

    def handle_locked_user(self):
        lockout_start_time = self.request.session.get("lockout_start_time")
        if lockout_start_time:
            lockout_start_time = tz.datetime.fromisoformat(lockout_start_time)
            now = tz.now()
            time_passed = (now - lockout_start_time).total_seconds()
            time_left = (self.lockout_duration * 60) - time_passed
            minutes_left = int(time_left // 60)
            seconds_left = int(time_left % 60)
            if time_left > 0:
                messages.error(
                    self.request,
                    _(
                        f"Too many post requests. Please wait {minutes_left} minutes and {seconds_left} seconds before trying again."
                    ),
                )
            else:
                self.request.session["max_counter"] = 0
                del self.request.session["lockout_start_time"]

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Handle OTP verification through POST requests."""
        count = request.session.get("max_counter", 0)
        block = self.request.session.get("block_count", 0)
        if self.block_count <= block:
            self.block_user()
            messages.error(
                self.request,
                _("You have been blocked due to multiple failed OTP attempts."),
            )
            return redirect(request.path)

        if not self.locked_user(count):
            request.session["max_counter"] = count + 1
            entered_otp = request.POST.get("verify_code")
            user = self.verify_otp(self.user_identifier, entered_otp)
            if user:
                if self.reason == ReasonOptions.FORGET_PASSWORD:
                    pass
                else:
                    login(request, user)
                self.clear_session_keys(["spa", "block_count", "max_counter"])
                return redirect(self.get_success_url())
            return self.render_to_response(self.get_context_data())
        else:
            if not self.request.session.get("lockout_start_time"):
                request.session["lockout_start_time"] = tz.now().isoformat()
                request.session["block_count"] = block + 1
            return self.handle_locked_user()

    def get_success_url(self):
        """Return the success URL if defined, else raise an error."""
        if not self.success_url:
            raise ValueError("The success_url attribute is not set.")
        return self.success_url

    def send_new_otp(self, user):
        """Send a new OTP to the user's email or phone number based on the
        identifier.
        """
        if "@" in self.user_identifier:
            otp_data = self.otp_manager.get_or_create_otp(
                identifier=user.id, reason=self.reason
            )
            send_email_otp(otp_data[0].token, user.email)
            messages.info(self.request, f"New OTP sent to your email: {user.email}")
        else:
            otp_data = self.otp_manager.get_or_create_otp(
                identifier=user.id, reason=self.reason
            )
            sms_obj = get_backends()
            sms_obj.send_one_message(str(user.phone_number), otp_data[0].token)
            messages.info(
                self.request,
                _(f"New OTP sent to your phone number: {user.phone_number}"),
            )

    def get_context_data(self, **kwargs):
        context = kwargs or {}
        context["minutes_left_expiry"] = self.minutes_left_expiry
        context["seconds_left_expiry"] = self.seconds_left_expiry
        return context

    def block_user(self):
        """Block the user and remove all OTP instances associated with them."""
        user = self.get_user_by_identifier()
        user.is_block = True
        user.is_active = False
        user.save()
        reason = self.request.session.get("reason")
        otp_instance = self.otp_manager.get_otp(identifier=user.id, reason=reason)
        otp_instance.state = OTPState.EXPIRED
        otp_instance.save()

    def get_user_by_identifier(self):
        """Retrieve the user based on their identifier email or phone number."""
        if "@" in self.user_identifier:
            return SageUser.objects.get(email=self.user_identifier)
        return SageUser.objects.get(phone_number=self.user_identifier)

    def clear_session_keys(self, keys):
        """Helper method to clear specified keys from the session."""
        for key in keys:
            if key in self.request.session:
                del self.request.session[key]
