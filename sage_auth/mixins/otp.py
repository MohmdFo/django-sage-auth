# views/otp_verification_view.py

from django.views import View
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from sage_otp.helpers.choices import ReasonOptions
from sage_auth.repository.services import OTPVerificationService


class VerifyOtpMixin(View):
    reason = ReasonOptions.EMAIL_ACTIVATION
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        self.service = OTPVerificationService(request, self.user_identifier, self.reason)
        user = self.service.get_user_by_identifier()

        if not user:
            messages.error(request, _("User not found. Please restart the process."))
            return redirect(request.path)

        if user.is_block:
            messages.error(request, _("Your account has been blocked. Please contact support."))
            return redirect(settings.LOGIN_URL)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        entered_otp = request.POST.get("verify_code")
        user = self.service.get_user_by_identifier()

        if not user:
            messages.error(request, _("Invalid user identifier."))
            return render(request, "otp_verification.html")

        result = self.service.verify_otp(user, entered_otp)

        if result["success"]:
            if result["status"] == "verified":
                messages.success(request, _("OTP verified successfully. You can now proceed."))
                return redirect(self.get_success_url())
        else:
            if result["status"] == "expired":
                messages.error(request, _("Your OTP has expired. A new OTP has been sent to your registered contact."))
            elif result["status"] == "max_attempts":
                messages.error(request, _("Too many incorrect attempts. A new OTP has been sent to your registered contact."))
            elif result["status"] == "incorrect":
                messages.error(request, _("Incorrect OTP. Please try again."))
            elif result["status"] == "invalid":
                messages.error(request, _("Invalid OTP. Please try again or restart the process."))
            elif result["status"] == "error":
                messages.error(request, _("An unexpected error occurred during OTP verification. Please try again later."))

        return render(request, "otp_verification.html")

    def get_success_url(self):
        if not self.success_url:
            raise ValueError("The success_url attribute is not set.")
        return self.success_url
