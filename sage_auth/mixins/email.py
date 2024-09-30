from django.shortcuts import redirect
from django.contrib import messages
from sage_otp.repository.managers.otp import OTPManager
from sage_otp.helpers.choices import ReasonOptions
from sage_auth.utils import send_email_otp
from sage_auth.models import CustomUser

class EmailMixin:
    """Mixin to handle OTP generation and sending for email verification."""

    otp_manager = OTPManager()

    def send_otp(self,otp,email):
        """Send OTP to the user's email."""
        send_email_otp(otp, email)

    def handle_otp(self, user):
        """Generate and send OTP if email is the USERNAME_FIELD."""
        otp_data = self.otp_manager.get_or_create_otp(
            identifier=user.id, 
            reason=ReasonOptions.EMAIL_ACTIVATION
        )
        print(f"Generated OTP: {otp_data[0].token}")
        self.send_otp(otp_data[0].token,user.email)
        messages.info(self.request, f"Verification code was sent to your email: {user.email}")
        return user.email

    def form_valid(self,user):
        """Handle OTP logic after the user is created."""

        email = self.handle_otp(user)
        return email
