from django.contrib.auth.signals import (
    user_logged_in,
    user_login_failed
)
from django.dispatch import Signal, receiver
from django.contrib.auth import get_user_model

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
    security,_ = LoginAttempt.objects.get_or_create(user=user)
    security.increment_total_logins()
    if user.is_staff or user.is_superuser:
        security.increment_admin_logins()


@receiver(user_login_failed)
def handle_failed_login(sender, credentials, **kwargs):
    User = get_user_model()
    username_field, _ = User.USERNAME_FIELD, User.REQUIRED_FIELDS
    try:
        user = User.objects.get(**{username_field: credentials['username']})
    except User.DoesNotExist:
        user = None
    if user:
        security, created = LoginAttempt.objects.get_or_create(user=user)
        security.increment_failed_attempts()
