from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django.views import View
from sage_otp.helpers.choices import OTPState, ReasonOptions
from sage_otp.helpers.exceptions import InvalidTokenException, OTPExpiredException
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.models import SageUser
from sage_auth.utils import send_email_otp, send_sms


class VerifyOtpMixin(View):
    """Mixin to verify OTP entered by the user, compatible with Django views."""

    otp_manager = OTPManager()
    user_identifier = None
    lockout_duration = getattr(settings, "OTP_LOCKOUT_DURATION", 3)
    lock_user = getattr(settings, "OTP_MAX_REQUEST_TIMEOUT", 10)
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
        if not self.reactivate_process:
            if not request.session.get("spa"):
                return HttpResponse("You cannot access this page.", status=403)
        return super().dispatch(request, *args, **kwargs)

    def verify_otp(self, user_identifier, entered_otp):
        """Verify OTP and activate the user if it matches."""
        try:
            if "@" in self.user_identifier:
                user = SageUser.objects.get(email=user_identifier)
            else:
                user = SageUser.objects.get(phone_number=user_identifier)
            session_search = self.request.session.get("reason")
            if session_search:
                self.reason = session_search
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
                messages.error(
                    self.request,
                    _("Your Time has Finished. We will send you a new OTP."),
                )
                self.send_new_otp(user)
                return False

            self.minutes_left_expiry = int(time_left_to_expire // 60)
            self.seconds_left_expiry = int(time_left_to_expire % 60)
            messages.info(
                self.request,
                _(
                    f"You have {self.minutes_left_expiry} minutes and {self.seconds_left_expiry} seconds left to enter the OTP."
                ),
            )
            if otp_instance.failed_attempts_count >= otp_max:
                otp_instance.update_state(OTPState.EXPIRED)
                messages.error(
                    self.request,
                    _(
                        "You have exceeded the maximum allowed OTP attempts.We will send a new OTP."
                    ),
                )
                self.send_new_otp(user)
                return False

            if otp_instance.token == entered_otp:
                user.is_active = True
                otp_instance.state = OTPState.CONSUMED
                user.save()
                otp_instance.save()
                messages.success(
                    self.request,
                    _(
                        "Your OTP was successfully verified. Your account is now active."
                    ),
                )
                return user

            else:
                otp_instance.failed_attempts_count += 1
                otp_instance.save()
                messages.error(self.request, "The OTP entered is incorrect.")
                return False

        except OTPExpiredException:
            messages.error(
                self.request, _("The OTP has expired. Please request a new one.")
            )
        except InvalidTokenException:
            messages.error(self.request, _("The OTP entered is incorrect."))
        except SageUser.DoesNotExist:
            messages.error(self.request, "No user found with this email or identifier.")

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
        if not self.locked_user(count):
            request.session["max_counter"] = count + 1
            entered_otp = request.POST.get("verify_code")
            user = self.verify_otp(self.user_identifier, entered_otp)
            if user:
                if self.reason == ReasonOptions.FORGET_PASSWORD:
                    pass
                else:
                    login(request, user)
                if request.session.get("spa"):
                    del request.session["spa"]
                return redirect(self.get_success_url())
            return self.render_to_response(self.get_context_data())

        else:
            if not self.request.session.get("lockout_start_time"):
                request.session["lockout_start_time"] = tz.now().isoformat()
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
            sms_obj = send_sms()
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
