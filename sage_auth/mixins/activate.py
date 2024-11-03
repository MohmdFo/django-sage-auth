import logging
from django.contrib import messages
from datetime import timezone, timedelta
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured
from sage_auth.utils.email_sender import ActivationEmailSender
from django.utils import timezone as django_timezone
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
import base64

logger = logging.getLogger(__name__)
User = get_user_model()

class ActivateAccountMixin(View):
    """
    Mixin to handle user account activation via token-based links.

    This class provides the `get` method to verify the token and activate
    the user's account if the token is valid. If the token has expired,
    a new activation email is sent to the user.
    """

    success_url = None
    register_url = None

    def dispatch(self, request, *args, **kwargs):
        """
        Ensure required URLs are set before processing the request.

        Raises:
            ImproperlyConfigured: If `success_url` is not set.
        """
        if not self.success_url:
            logger.error("The 'success_url' attribute must be set.")
            raise ImproperlyConfigured(
                "The 'success_url' attribute must be set."
            )
        if not self.register_url:
            logger.error("The 'register_url' attribute must be set.")
            raise ImproperlyConfigured(
                "The 'register_url' attribute must be set."
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uidb64, token, ts):
        """
        Handle GET requests for account activation.
        Decodes the user's ID from `uidb64`, verifies the activation `token`,
        and activates the user's account if valid. If the link has expired,
        a new activation email is sent.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
            timestamp = int(base64.urlsafe_b64decode(ts).decode())
            expire = getattr(settings, "ACTIVATION_LINK_EXPIRY_MINUTES", 1)
            expiry_duration = timedelta(minutes=expire)

            if django_timezone.now() - django_timezone.datetime.fromtimestamp(
                timestamp, tz=timezone.utc
            ) > expiry_duration:
                logger.warning(
                    "Activation link expired for user %s. Sending a new email.", 
                    user.email
                )
                ActivationEmailSender().send_activation_email(user, request)
                return HttpResponse(
                    "The activation link expired. A new activation email has been sent."
                )

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                logger.info(
                    "User %s has been successfully activated.", user.email
                )
                messages.success(
                    request,
                    "Your account has been activated successfully. You can now log in."
                )
                return redirect(self.success_url)
            else:
                logger.warning(
                    "Invalid activation token for user %s.",
                    user.email
                )
        except (ValueError, OverflowError) as e:
            logger.error("Error in activation link processing: %s", e)
            messages.error(
                request, "The activation link is invalid or has expired."
            )
            return redirect(self.register_url)
