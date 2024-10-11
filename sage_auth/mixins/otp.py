from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils import timezone as tz
from django.views import View
from sage_otp.helpers.choices import OTPState, ReasonOptions
from sage_otp.helpers.exceptions import InvalidTokenException, OTPExpiredException
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.models import CustomUser
from sage_auth.utils import send_email_otp


class VerifyOtpMixin(View):
    """Mixin to verify OTP entered by the user, compatible with Django views."""

    otp_manager = OTPManager()
    user_identifier = None
    lockout_duration = getattr(settings, "OTP_LOCKOUT_DURATION", 3)
    reason = ReasonOptions.EMAIL_ACTIVATION
    success_url = None

    def verify_otp(self, user_identifier, entered_otp):
        """Verify OTP and activate the user if it matches."""
        try:
            user = CustomUser.objects.get(email=user_identifier)
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
                    self.request, "Your Time has Finished. We will send you a new OTP."
                )
                otp_data = self.otp_manager.get_or_create_otp(
                    identifier=user.id, reason=self.reason
                )
                send_email_otp(otp_data[0].token, user.email)
                messages.info(self.request, f"New OTP sent to your email: {user.email}")
                return False

            minutes_left_expiry = int(time_left_to_expire // 60)
            seconds_left_expiry = int(time_left_to_expire % 60)
            messages.info(
                self.request,
                f"You have {minutes_left_expiry} minutes and {seconds_left_expiry} seconds left to enter the OTP.",
            )

            if otp_instance.failed_attempts_count >= otp_max:
                otp_instance.update_state(OTPState.EXPIRED)
                messages.error(
                    self.request,
                    "You have exceeded the maximum allowed OTP attempts.We will send a new OTP.",
                )
                otp_data = self.otp_manager.get_or_create_otp(
                    identifier=user.id, reason=self.reason
                )
                send_email_otp(otp_data[0].token, user.email)
                messages.info(
                    self.request,
                    f"New Verification code was sent to your email: {user.email}",
                )
                return False

            if otp_instance.token == entered_otp:
                user.is_active = True
                otp_instance.state = OTPState.CONSUMED
                user.save()
                otp_instance.save()
                messages.success(
                    self.request,
                    "Your OTP was successfully verified. Your account is now active.",
                )
                return user

            else:
                otp_instance.failed_attempts_count += 1
                otp_instance.save()
                messages.error(self.request, "The OTP entered is incorrect.")
                return False

        except OTPExpiredException:
            messages.error(
                self.request, "The OTP has expired. Please request a new one."
            )
        except InvalidTokenException:
            messages.error(self.request, "The OTP entered is incorrect.")
        except CustomUser.DoesNotExist:
            messages.error(self.request, "No user found with this email or identifier.")

        return False

    def locked_user(self, count):
        return count >= 10

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
                    f"Too many post requests. Please wait {minutes_left} minutes and {seconds_left} seconds before trying again.",
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
            print(request.session.get("max_counter", 0))
            entered_otp = request.POST.get("verify_code")
            user = self.verify_otp(self.user_identifier, entered_otp)

            if user:
                if self.reason == ReasonOptions.FORGET_PASSWORD:
                    print("Y")
                else:
                    login(request, user)
                del request.session["email"]
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
