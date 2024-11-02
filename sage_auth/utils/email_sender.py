from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import base64


def send_email_otp(token, email):
    """
    Sends a One-Time Password (OTP) to a specified email address for 
    verification purposes.
    This function retrieves the email template for OTP verification, 
    formats it with the provided token, and sends it using 
    Django's email backend.
    The sender's email address is configured in Django settings.
    """
    subject = "Email Verification"
    message = render_to_string(
        "email_verification_template.html", {"verification_code": token}
    )
    from_email = getattr(settings, "EMAIL_HOST_USER", None)
    recipient_list = [email]

    send_mail(
        subject,
        "",
        from_email,
        recipient_list,
        html_message=message,
        fail_silently=False,
    )

class ActivationEmailSender:
    """
    Handles the creation and sending of account activation emails for users.
    This class generates a unique token-based activation link, which is then 
    embedded into an email message. The link allows the user to activate their 
    account by clicking it, verifying their identity in the process.
    """
    def send_activation_email(self, user, request):
        # Generate token, UID, and timestamp
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        timestamp = int(timezone.now().timestamp())
        encoded_timestamp = base64.urlsafe_b64encode(str(timestamp).encode()).decode()
        url = getattr(settings,"ACTIVATION_LINK_NAME","activate")
        activation_link = reverse(url, kwargs={"uidb64": uid, "token": token, "ts": encoded_timestamp})
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
