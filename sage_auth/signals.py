from django.dispatch import Signal

# Login Scenarios
user_login_attempt = Signal()
user_login_failed = Signal()
user_otp_sent = Signal()
user_otp_verified = Signal()

# Register Scenarios
user_registered = Signal()
user_activated = Signal()
activation_failed = Signal()

# OTP Scenarios
otp_generated = Signal()
otp_verified = Signal()
otp_expired = Signal()
otp_failed = Signal()
