import secrets

from django.conf import settings
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from sage_sms.factory import SMSBackendFactory


def otpCreate():
    number = secrets.randbelow(90000) + 10000
    return str(number)


def send_email_otp(token, email):
    subject = "Email Verification"
    message = render_to_string(
        "email_verification_template.html", {"verification_code": token}
    )
    from_email = getattr(settings,"EMAIL_HOST_USER", None)
    recipient_list = [email]

    send_mail(
        subject,
        "",
        from_email,
        recipient_list,
        html_message=message,
        fail_silently=False,
    )


def set_required_fields():
    """
    Dynamically set the USERNAME_FIELD and REQUIRED_FIELDS base
    on settings.
    """

    username_field = None
    required_fields = []

    for method in settings.AUTHENTICATION_METHODS:
        if settings.AUTHENTICATION_METHODS[method]:
            if username_field is None:
                if method == "EMAIL_PASSWORD":
                    username_field = "email"
                elif method == "PHONE_PASSWORD":
                    username_field = "phone_number"
                elif method == "USERNAME_PASSWORD":
                    username_field = "username"
            else:
                if method == "EMAIL_PASSWORD":
                    required_fields.append("email")
                elif method == "PHONE_PASSWORD":
                    required_fields.append("phone_number")
                elif method == "USERNAME_PASSWORD":
                    required_fields.append("username")

    required_fields = list(set(required_fields))

    return username_field, required_fields


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


account_activation_token = AccountActivationTokenGenerator()


class ActivationEmailSender:
    """Utility to send account activation email."""

    def send_activation_email(self, user, request,url="activate"):
        # Create the token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build the activation link
        activation_link = reverse(url, kwargs={"uidb64": uid, "token": token})
        activation_url = f"{request.scheme}://{request.get_host()}{activation_link}"

        subject = "Activate Your Account"
        message = render_to_string(
            "activation_email.html",
            {
                "user": user,
                "activation_url": activation_url,
            },
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_sms():
    factory = SMSBackendFactory(settings.SMS_CONFIGS, "sage_auth.backends")
    sms_provider_class = factory.get_backend()
    sms_provider = sms_provider_class(settings)
    return sms_provider
