from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from sage_otp.helpers.choices import OTPState, ReasonOptions
from sage_otp.helpers.exceptions import OTPDoesNotExists
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.mixins import EmailMixin, VerifyOtpMixin
from sage_auth.mixins.phone import PhoneOtpMixin
from sage_auth.models import SageUser
from sage_auth.utils import ActivationEmailSender, set_required_fields

User = get_user_model()


class ResendJsonMixin(View, EmailMixin):
    """
    Mixin to handle account reactivation requests by generating a new OTP or
    activation link for the user, if an active OTP does not already exist.

    This mixin checks if an OTP for reactivation is already active. If not, it
    initiates a new OTP or sends an activation link based on the authentication
    method defined in settings. This supports both email and phone number
    reactivation.
    """

    otp_manager = OTPManager()
    reason = ReasonOptions.EMAIL_ACTIVATION

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        if self.user_identifier is None:
            raise PermissionDenied("You have been blocked")
        self.reason = request.session.get("reason", ReasonOptions.EMAIL_ACTIVATION)
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username_field, __ = set_required_fields()

        try:
            user = User.objects.get(**{username_field: self.user_identifier})
            if self.reason == ReasonOptions.EMAIL_ACTIVATION:
                if username_field == "phone_number":
                    self.reason = ReasonOptions.PHONE_NUMBER_ACTIVATION
            try:
                otp_instance = self.otp_manager.get_otp(
                    identifier=user.id, reason=self.reason
                )

                if otp_instance.state == OTPState.ACTIVE:
                    message = _("An active OTP already exists. Please check your phone for the verification code.")
                else:
                    self.create_new_otp_or_activation_link(user, request)
                    message = _("OTP has been resent successfully.")
            except OTPDoesNotExists:
                self.create_new_otp_or_activation_link(user, request)
                message = _("OTP has been resent successfully.")

            response = {"status": "success", "message": message}

        except SageUser.DoesNotExist:
            response = {"status": "error", "message": _("No user found with this email.")}

        # Check if the request is an AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(response)

        # Fallback for standard requests
        messages.add_message(request, messages.INFO if response["status"] == "success" else messages.ERROR, response["message"])
        return redirect(request.META.get("HTTP_REFERER", "/"))

    def create_new_otp_or_activation_link(self, user, request):
        if settings.SEND_OTP:
            self.email = self.send_otp_based_on_strategy(user)
            self.request.session["email"] = self.email
            self.request.session.save()
        elif settings.USER_ACCOUNT_ACTIVATION_ENABLED:
            ActivationEmailSender().send_activation_email(user, request)

    def send_otp_based_on_strategy(self, user):
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(self, user,self.reason)
        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            self.request.session["reason"] = ReasonOptions.PHONE_NUMBER_ACTIVATION
            return sms_obj.send_sms_otp(user)


class ResendMixin(View,EmailMixin):
    """
    Mixin for handling resend requests for OTP or activation links.
    """

    otp_manager = OTPManager()
    reason = ReasonOptions.EMAIL_ACTIVATION

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        if not self.user_identifier:
            raise PermissionDenied("You have been blocked")
        self.reason = request.session.get("reason", ReasonOptions.EMAIL_ACTIVATION)
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username_field, __ = set_required_fields()

        try:
            user = User.objects.get(**{username_field: self.user_identifier})
            if self.reason == ReasonOptions.EMAIL_ACTIVATION:
                if username_field == "phone_number":
                    self.reason = ReasonOptions.PHONE_NUMBER_ACTIVATION
            try:
                otp_instance = self.otp_manager.get_otp(
                    identifier=user.id, reason=self.reason
                )

                if otp_instance.state == OTPState.ACTIVE:
                    messages.info(
                        request,
                        _(
                            "An active OTP already exists. Please check your phone for the verification code."
                        ),
                    )
                else:
                    self.create_new_otp_or_activation_link(user, request)

            except OTPDoesNotExists:
                self.create_new_otp_or_activation_link(user, request)
                messages.success(request, _("OTP has been resent successfully."))
        except SageUser.DoesNotExist:
            messages.error(request, _("No user found with this email."))

        return redirect(request.META.get("HTTP_REFERER", "/"))

    def create_new_otp_or_activation_link(self, user, request):
        if settings.SEND_OTP:
            self.email = self.send_otp_based_on_strategy(user)
            self.request.session["email"] = self.email
            self.request.session.save()
        elif settings.USER_ACCOUNT_ACTIVATION_ENABLED:
            ActivationEmailSender().send_activation_email(user, request)
            messages.success(
                request,
                _("Please check your email to activate your account."),
            )

    def send_otp_based_on_strategy(self, user):
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(self, user,self.reason)
        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            sms_obj = PhoneOtpMixin()
            return sms_obj.send_sms_otp(user,self.reason)
