import logging

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from sage_otp.helpers.choices import ReasonOptions
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.utils import send_email_otp

logger = logging.getLogger(__name__)


class EmailMixin:
    """
    Mixin for handling OTP (One-Time Password) generation and dispatch for
    email-based verification processes.

    This mixin is designed to integrate OTP functionality within views that
    require user verification, such as account activation, password reset, or
    login. It leverages Django's messaging framework to notify users about OTP
    dispatch and can be extended for custom behaviors.
    """

    otp_manager = OTPManager()

    def send_otp(self, otp, email):
        """Send OTP to the user's email."""
        send_email_otp(otp, email)

    def handle_otp(self, user, reason):
        """Generate and send OTP if email is the USERNAME_FIELD."""
        logger.debug("Generating OTP for user ID: %s, reason: %s", user.id, reason)

        otp_data = self.otp_manager.get_or_create_otp(identifier=user.id, reason=reason)

        self.send_otp(otp_data[0].token, user.email)
        logger.debug("Sending OTP to email: %s", user.email)

        messages.info(
            self.request, _(f"Verification code was sent to your email: {user.email}")
        )
        return user.email

    def form_valid(self, user, reason=ReasonOptions.EMAIL_ACTIVATION):
        """Handle OTP logic after the user is created."""
        email = self.handle_otp(user, reason)
        logger.info("OTP handling successful for user: %s", user.email)

        return email
