import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import LoginView
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from sage_otp.helpers.choices import ReasonOptions
from sage_auth.mixins.email import EmailMixin
from sage_auth.mixins.otp import VerifyOtpMixin
from sage_auth.mixins.phone import PhoneOtpMixin
from sage_auth.utils import set_required_fields
from sage_auth.signals import (
    user_login_attempt,
    user_login_failed,
    user_otp_sent,
    user_otp_verified
)

logger = logging.getLogger(__name__)

User = get_user_model()


class LoginOtpMixin(FormView, EmailMixin):
    template_name = None
    form_class = None

    def form_valid(self, form):
        identifier = form.cleaned_data.get("login_field")
        user = self.get_user(identifier)

        if user:
            self.request.session["email"] = identifier
            self.send_otp_based_on_strategy(user)
            self.request.session.save()
            self.request.session["spa"] = True

            # Trigger user_otp_sent signal
            user_otp_sent.send(
                sender=self.__class__,
                user=user,
                identifier=identifier,
                method="email" if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD") else "phone",
                reason=ReasonOptions.LOGIN,
            )
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, _("No user found with this information."))
            return redirect(self.get_success_url())

    def get_user(self, identifier):
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return User.objects.filter(email=identifier).first()
        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            return User.objects.filter(phone_number=identifier).first()
        return None

    def send_otp_based_on_strategy(self, user):
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(self, user=user, reason=ReasonOptions.LOGIN)

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            messages.info(
                self.request, f"OTP sent to your phone number: {user.phone_number}"
            )
            return sms_obj.send_sms_otp(user, ReasonOptions.LOGIN)

class LoginOtpVerifyMixin(VerifyOtpMixin, TemplateView):
    template_name = "None"
    success_url = None

    def post(self, request, *args, **kwargs):
        self.request.session["reason"] = ReasonOptions.LOGIN
        response = super().post(request, *args, **kwargs)

        user = self.get_user()  # Assume `get_user` retrieves the user object based on session or form data
        identifier = self.request.session.get("email")
        otp_success = self.verify_otp(user)  # Custom method to validate OTP

        # Trigger user_otp_verified signal
        user_otp_verified.send(
            sender=self.__class__,
            user=user,
            identifier=identifier,
            success=otp_success,
        )
        return response

class SageLoginMixin(LoginView):
    template_name = None
    success_url = None
    reactivate_url = None

    def dispatch(self, request, *args, **kwargs):
        if not self.success_url:
            raise ImproperlyConfigured("The 'success_url' attribute must be set.")
        if not self.reactivate_url:
            raise ImproperlyConfigured("The 'reactivate_url' attribute must be set.")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        identifier = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        username_field, __ = set_required_fields()

        try:
            user = User.objects.get(**{username_field: identifier})
            if not check_password(password, user.password):
                user_login_attempt.send(sender=self.__class__, user=user, identifier=identifier, success=False)
                messages.error(self.request, _("Invalid username or password. Please try again."))
                return super().form_invalid(form)
        except User.DoesNotExist:
            messages.error(self.request, _("Invalid username or password. Please try again."))
            user = None

        if user is not None:
            if user.is_block:
                messages.error(
                    self.request,
                    _("Your account has been blocked for security reasons."),
                )
                raise PermissionDenied("You have been blocked")
            if not user.is_active:
                messages.error(
                    self.request,
                    _("Your account is not activated. Please check your phone number or email."),
                )
                self.request.session["email"] = identifier
                user_login_attempt.send(sender=self.__class__, user=user, identifier=identifier, success=False)
                return redirect(self.reactivate_url)
            else:
                user_login_attempt.send(sender=self.__class__, user=user, identifier=identifier, success=False)
                return super().form_invalid(form)
        else:
            return super().form_invalid(form)


    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        identifier = form.cleaned_data.get("username")
        user_login_attempt.send(sender=self.__class__, user=user, identifier=identifier, success=True)
        return response

    def get_success_url(self):
        return self.success_url
