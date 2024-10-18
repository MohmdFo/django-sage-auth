from django.contrib import messages
from sage_otp.helpers.choices import ReasonOptions
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.utils import send_sms


class PhoneOtpMixin:
    """Mixin to handle OTP generation and sending for email verification."""

    otp_manager = OTPManager()

    def send_otp(self, otp,phone):
        """Send OTP to the user's phone."""
        obj = send_sms()
        obj.send_one_message(phone,otp)

    def handle_otp(self, user,reason):
        """Generate and send OTP if phone is the USERNAME_FIELD."""
    
        otp_data = self.otp_manager.get_or_create_otp(
            identifier=user.id,
            reason=reason
        )
        self.send_otp(otp_data[0].token,str(user.phone_number))
        return str(user.phone_number)

    def send_sms_otp(self, user,reason=ReasonOptions.PHONE_NUMBER_ACTIVATION):
        """Handle OTP logic after the user is created."""
        phone = self.handle_otp(user,reason)
        return phone
