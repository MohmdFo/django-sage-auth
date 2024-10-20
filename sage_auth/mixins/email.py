from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from sage_otp.helpers.choices import ReasonOptions
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.utils import send_email_otp


class EmailMixin:
    """Mixin to handle OTP generation and sending for email verification."""

    otp_manager = OTPManager()

    def send_otp(self, otp, email):
        """Send OTP to the user's email."""
        send_email_otp(otp, email)

    def handle_otp(self, user, reason):
        """Generate and send OTP if email is the USERNAME_FIELD."""

        otp_data = self.otp_manager.get_or_create_otp(identifier=user.id, reason=reason)

        self.send_otp(otp_data[0].token, user.email)
        messages.info(
            self.request, _(f"Verification code was sent to your email: {user.email}")
        )
        return user.email

    def form_valid(self, user, reason=ReasonOptions.EMAIL_ACTIVATION):
        """Handle OTP logic after the user is created."""
        email = self.handle_otp(user, reason)
        return email
