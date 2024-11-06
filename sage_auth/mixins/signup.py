import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from sage_otp.helpers.choices import ReasonOptions

from sage_auth.mixins.email import EmailMixin
from sage_auth.mixins.phone import PhoneOtpMixin
from sage_auth.utils import ActivationEmailSender

logger = logging.getLogger(__name__)


class UserCreationMixin(CreateView, EmailMixin):
    """
    Mixin for creating a new user account with optional OTP (email or phone)
    verification and activation link functionality.

    This mixin builds upon Django's CreateView to support secure user creation
    with multiple verification strategies. Based on the configured settings, it
    either sends an OTP via email or SMS or generates an account activation link.
    It checks the user's login status, handles form validation, and ensures
    account activation through email or OTP mechanisms.
    """

    success_url = None
    form_class = None
    template_name = None
    email = None
    already_login_url = None

    def dispatch(self, request, *args, **kwargs):
        """Ensure required URLs are set before processing the request."""
        if not self.already_login_url:
            raise ImproperlyConfigured("The 'already_login_url' attribute must be set.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle form validation, save the user, and log them in."""
        user = form.save()
        form.instance.id = user.id
        user.is_active = False
        user.save()
        logger.info("User created but not activated: %s", user)
        if settings.SEND_OTP:
            self.email = self.send_otp_based_on_strategy(user)
            self.request.session["email"] = self.email
            self.request.session["spa"] = True
            self.request.session.save()

        elif settings.USER_ACCOUNT_ACTIVATION_ENABLED:
            user.is_active = False
            user.save()
            ActivationEmailSender().send_activation_email(user, self.request)
            messages.success(
                self.request,
                _(
                    "Account created successfully. Please check your email to activate your account."
                ),
            )
            logger.info("Activation email sent to: %s", user.email)

            return HttpResponse("Activation link sent to your email address")

        return redirect(self.get_success_url())

    def send_otp_based_on_strategy(self, user):
        """Send OTP based on the strategy in settings.AUTHENTICATION_METHODS."""

        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(self, user)
        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            self.request.session["reason"] = ReasonOptions.PHONE_NUMBER_ACTIVATION
            messages.info(
                self.request, f"OTP sent to your phone number: {user.phone_number}"
            )
            return sms_obj.send_sms_otp(user)

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        logger.warning("Form submission invalid: %s", form.errors)
        messages.error(
            self.request,
            _("There was an error with your submission. Please check the form and try again.")
        )
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """Return the success URL."""
        if not self.success_url:
            logger.error("The success_url attribute is not set.")
            raise ValueError("The success_url attribute is not set.")
        return self.success_url

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, _("You are already logged in."))
            logger.info("Authenticated user attempting to access user creation view.")
            return redirect(self.already_login_url)
        return super().get(request, *args, **kwargs)
