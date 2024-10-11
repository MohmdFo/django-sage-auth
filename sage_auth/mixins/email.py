from django.contrib import messages
from sage_otp.helpers.choices import ReasonOptions
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.utils import send_email_otp


class EmailMixin:
    """Mixin to handle OTP generation and sending for email verification."""

    otp_manager = OTPManager()

    def send_otp(self, otp, email):
        """Send OTP to the user's email."""
        send_email_otp(otp, email)

    def handle_otp(self, user, kind=0):
        """Generate and send OTP if email is the USERNAME_FIELD."""
        if kind != 0:
            otp_data = self.otp_manager.get_or_create_otp(
                identifier=user.id, reason=ReasonOptions.FORGET_PASSWORD
            )
        else:
            otp_data = self.otp_manager.get_or_create_otp(
                identifier=user.id, reason=ReasonOptions.EMAIL_ACTIVATION
            )

        self.send_otp(otp_data[0].token, user.email)
        messages.info(
            self.request, f"Verification code was sent to your email: {user.email}"
        )
        return user.email

    def form_valid(self, user, kind=0):
        """Handle OTP logic after the user is created."""

        email = self.handle_otp(user, kind)
        return email
