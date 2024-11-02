import logging

from sage_otp.helpers.choices import ReasonOptions
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.utils import get_backends

logger = logging.getLogger(__name__)


class PhoneOtpMixin:
    """
    Mixin for handling OTP (One-Time Password) generation and sending
    for phone-based authentication.

    This mixin provides functionality to generate an OTP and send it
    to the user's phone number. It integrates with the OTPManager for OTP
    creation and utilizes the `get_backends` utility to dispatch the OTP
    via SMS.
    """

    otp_manager = OTPManager()

    def send_otp(self, otp, phone):
        """Send OTP to the user's phone."""
        logger.info("Attempting to send OTP to phone: %s", phone)
        obj = get_backends()
        obj.send_one_message(phone, otp)

    def handle_otp(self, user, reason):
        """Generate and send OTP."""
        logger.debug("Generating OTP for user: %s with reason: %s", user.id, reason)
        otp_data = self.otp_manager.get_or_create_otp(identifier=user.id, reason=reason)
        self.send_otp(otp_data[0].token, str(user.phone_number))
        return str(user.phone_number)

    def send_sms_otp(self, user, reason=ReasonOptions.PHONE_NUMBER_ACTIVATION):
        """Handle OTP logic after the user is created."""
        phone = self.handle_otp(user, reason)
        logger.info("SMS OTP sent to phone: %s", phone)
        return phone
