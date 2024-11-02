import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from sage_otp.helpers.choices import OTPState, ReasonOptions
from sage_otp.helpers.exceptions import OTPDoesNotExists
from sage_otp.repository.managers.otp import OTPManager

from sage_auth.mixins import EmailMixin, VerifyOtpMixin
from sage_auth.mixins.phone import PhoneOtpMixin
from sage_auth.models import SageUser
from sage_auth.utils import ActivationEmailSender, set_required_fields

logger = logging.getLogger(__name__)
User = get_user_model()


class ReactivationMixin(TemplateView, EmailMixin, VerifyOtpMixin):
    """
    Mixin to handle account reactivation requests by generating a new OTP or
    activation link for the user, if an active OTP does not already exist.

    This mixin checks if an OTP for reactivation is already active. If not, it
    initiates a new OTP or sends an activation link based on the authentication
    method defined in settings. This supports both email and phone number
    reactivation.
    """

    template_name = "None"
    success_url = None
    otp_manager = OTPManager()
    reason = ReasonOptions.EMAIL_ACTIVATION
    reactivate_process = True

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        logger.debug("User identifier set to: %s", self.user_identifier)

        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        username_field, __ = set_required_fields()

        try:
            user = User.objects.get(**{username_field: self.user_identifier})
            logger.info("User found: %s", user)

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
                    logger.info("Active OTP exists for user: %s", user)

                else:
                    self.create_new_otp_or_activation_link(user, request)

            except OTPDoesNotExists:
                self.create_new_otp_or_activation_link(user, request)

            return super().get(request, *args, **kwargs)

        except SageUser.DoesNotExist:
            logger.error("User not found with identifier: %s", self.user_identifier)
            messages.error(request, "No user found with this email.")
            return redirect(self.get_success_url())

    def create_new_otp_or_activation_link(self, user, request):
        if settings.SEND_OTP:
            self.email = self.send_otp_based_on_strategy(user)
            self.request.session["email"] = self.email
            self.request.session.save()

        elif settings.USER_ACCOUNT_ACTIVATION_ENABLED:
            ActivationEmailSender().send_activation_email(user, request)
            messages.success(
                self.request,
                "Please check your email to activate your account.",
            )
            logger.info("Activation link sent to user: %s", user)
            return HttpResponse("Activation link sent to your email address")

    def get_success_url(self):
        self.request.session["spa"] = True
        if not self.success_url:
            logger.error("The success_url attribute is not set.")
            raise ValueError("The success_url attribute is not set.")
        return self.success_url

    def send_otp_based_on_strategy(self, user):
        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            logger.info("Sending email-based OTP to user: %s", user)
            return EmailMixin.form_valid(self, user)

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            logger.info("Sending phone-based OTP to user: %s", user)
            sms_obj = PhoneOtpMixin()
            self.request.session["reason"] = ReasonOptions.PHONE_NUMBER_ACTIVATION
            return sms_obj.send_sms_otp(user)
