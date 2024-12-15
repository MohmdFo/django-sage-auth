from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import Signal, receiver

from .models import LoginAttempt

# Login Scenarios
user_login_attempt = Signal()
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


@receiver(user_logged_in)
def update_security_metrics(sender, request, user, **kwargs):
    """Create a new record for a successful login attempt."""
    LoginAttempt.objects.create(
        user=user,
        total_logins=1,
        admin_logins=1 if user.is_staff or user.is_superuser else 0,
        failed_attempts=0,
    )


@receiver(user_login_failed)
def handle_failed_login(sender, credentials, **kwargs):
    User = get_user_model()
    username_field, _ = User.USERNAME_FIELD, User.REQUIRED_FIELDS
    try:
        user = User.objects.get(**{username_field: credentials["username"]})
    except User.DoesNotExist:
        user = None
    if user:
        LoginAttempt.objects.create(
            user=user, total_logins=0, admin_logins=0, failed_attempts=1
        )
