import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from sage_otp.helpers.choices import ReasonOptions

from sage_auth.forms import PasswordResetForm, ResetPasswordConfrimForm
from sage_auth.mixins.email import EmailMixin
from sage_auth.mixins.otp import VerifyOtpMixin

logger = logging.getLogger(__name__)

User = get_user_model()


class ForgetPasswordMixin(FormView, EmailMixin):
    """
    Mixin that handles sending OTP (via email or SMS) for the forget password process.
    """

    template_name = None
    form_class = PasswordResetForm

    def form_valid(self, form):
        """Handle form validation, retrieve the user, and send OTP based on the strategy."""
        identifier = form.cleaned_data.get("identifier")
        user = self.get_user(identifier)

        if user:
            self.request.session["email"] = identifier
            self.send_otp_based_on_strategy(user)
            self.request.session.save()
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
            return EmailMixin.form_valid(self, user=user, kind=1)

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            return self.send_otp_sms(user.phone_number)

    def send_otp_sms(self, phone_number):
        pass


class ForgetPasswordConfirmMixin(VerifyOtpMixin, TemplateView):
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
    template_name = None
    page_name = "Password reset sent"
    success_url = None
    form_class = ResetPasswordConfrimForm

    def dispatch(self, request, *args, **kwargs):

        if not request.session.get("changing_password"):
            logger.warning(
                "Attempt to access password reset confirm view without changing password."
            )
            return redirect("login", permanent=False)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        identify = self.request.session.get("email")
        user = User.objects.get(email=identify)
        return form_class(user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        del self.request.session["changing_password"]
        messages.success(
            self.request,
            "Your password has been reset successfully. You can now login with your new password.",
        )
        logger.info("Password reset confirmed and form submitted successfully.")
        return super().form_valid(form)
