import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model,login
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from django.contrib.auth.views import LoginView

from sage_otp.helpers.choices import ReasonOptions
from sage_auth.utils import set_required_fields
from sage_auth.forms import OtpLoginFormMixin
from sage_auth.mixins.email import EmailMixin
from sage_auth.mixins.otp import VerifyOtpMixin
from sage_auth.mixins.phone import PhoneOtpMixin

logger = logging.getLogger(__name__)

User = get_user_model()


class LoginOtpMixin(FormView, EmailMixin):
    """
    Mixin that handles sending OTP (via email or SMS) for the forget password
    process.
    """

    template_name = None
    form_class = OtpLoginFormMixin

    def form_valid(self, form):
        """Handle form validation, retrieve the user, and send OTP based on the
        strategy.
        """
        identifier = form.cleaned_data.get("login_field")
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
            return EmailMixin.form_valid(self, user=user, reason=ReasonOptions.LOGIN)

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            messages.info(self.request, f"OTP sent to your phone number: {user.phone_number}")
            return sms_obj.send_sms_otp(user,ReasonOptions.LOGIN)

class LoginOtpVerifyMixin(VerifyOtpMixin, TemplateView):
    template_name = "None"
    success_url = None

    def post(self, request, *args, **kwargs):
        self.request.session["reason"] = ReasonOptions.LOGIN
        return super().post(request, *args, **kwargs)



class SageLoginMixin(LoginView):
    template_name= None
    success_url = None

    def form_invalid(self, form):
        identifier = form.cleaned_data.get("username")

        username_field, _ = set_required_fields()

        try:
            user = User.objects.get(**{username_field: identifier})
        except User.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                login(self.request, user)
                return redirect(self.success_url)
            else:
                messages.error(
                    self.request,
                    "Your account is not activated. Please check your phone number or email",
                )
                self.request.session["email"] = identifier
                return redirect("reactivate")
        else:
            return super().form_invalid(form)
    
    def get_success_url(self):
        return self.success_url
