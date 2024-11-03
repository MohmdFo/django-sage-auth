import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from sage_otp.helpers.choices import ReasonOptions

from sage_auth.mixins import EmailMixin, VerifyOtpMixin
from sage_auth.mixins.phone import PhoneOtpMixin
from sage_auth.utils import set_required_fields

logger = logging.getLogger(__name__)

User = get_user_model()


class ForgetPasswordMixin(FormView, EmailMixin):
    """
    Mixin to facilitate OTP-based password recovery.

    This mixin handles sending an OTP for the password recovery process, either
    by email or SMS, based on the configured authentication strategy. Once the
    OTP is sent, it redirects to a success URL for verification.
    """

    template_name = None
    form_class = None

    def form_valid(self, form):
        """Handle form validation, retrieve the user, and send OTP based on the
        strategy.
        """
        identifier = form.cleaned_data.get("identifier")
        user = self.get_user(identifier)

        if user:
            self.request.session["email"] = identifier
            self.send_otp_based_on_strategy(user)
            self.request.session.save()
            self.request.session["spa"] = True

            return redirect(self.get_success_url())
        else:
            messages.error(self.request, _("No user found with this information."))
            return redirect(self.get_success_url())

    def get_user(self, identifier):
        """Retrieve the user based on the identifier (email or phone number)."""
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return User.objects.filter(email=identifier).first()
        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            return User.objects.filter(phone_number=identifier).first()
        return None

    def send_otp_based_on_strategy(self, user):
        """Send OTP based on the strategy in settings.AUTHENTICATION_METHODS."""
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(
                self, user=user, reason=ReasonOptions.FORGET_PASSWORD
            )

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            messages.info(
                self.request, _(f"OTP sent to your phone number: {user.phone_number}")
            )
            return sms_obj.send_sms_otp(user, ReasonOptions.FORGET_PASSWORD)


class ForgetPasswordConfirmMixin(VerifyOtpMixin, TemplateView):
    """
    Mixin to handle OTP verification for password recovery.

    This mixin verifies the OTP provided by the user to
    ensure the password reset.
    request is valid. It utilizes the `VerifyOtpMixin`
    to check OTP validity and  enables the password reset process upon
    successful OTP confirmation.
    """

    template_name = "None"
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.reason = ReasonOptions.FORGET_PASSWORD
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.request.session["changing_password"] = True
        self.request.session["reason"] = ReasonOptions.FORGET_PASSWORD
        return super().post(request, *args, **kwargs)


class ForgetPasswordDoneMixin(FormView):
    """
    Mixin to finalize the password reset process after OTP verification.

    This mixin provides a view for users to complete the password reset process
    after OTP verification. It ensures that a password reset is in progress and
    directs users to a successful reset page upon completion.
    """

    template_name = None
    page_name = "Password reset sent"
    success_url = None
    form_class = None
    no_access_url = None

    def dispatch(self, request, *args, **kwargs):
        if not self.no_access_url:
            raise ImproperlyConfigured("The 'no_access_url' attribute must be set.")
        if not request.session.get("changing_password"):
            logger.warning(
                "Attempt to access password reset confirm view without changing password."
            )
            return redirect(self.no_access_url, permanent=False)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        identify = self.request.session.get("email")
        username_field, _ = set_required_fields()

        user = User.objects.get(**{username_field: identify})

        return form_class(user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        del self.request.session["changing_password"]
        messages.success(
            self.request,
            _(
                "Your password has been reset successfully. You can now login with your new password."
            ),
        )
        logger.info("Password reset confirmed and form submitted successfully.")
        return super().form_valid(form)


class PasswordChangeMixin(LoginRequiredMixin, PasswordChangeView):
    """
    A mixin for handling password changes for logged-in users, utilizing Django's
    built-in PasswordChangeView for handling GET and POST requests.
    """

    form_class = PasswordChangeForm
    template_name = None
    success_url = None


class PasswordChangeDoneMixin(LoginRequiredMixin, PasswordChangeDoneView):
    """
    A mixin for handling the password change confirmation page after
    a successful password update utilizing Django's built-in.

    PasswordChangeDoneView.
    """

    template_name = None
