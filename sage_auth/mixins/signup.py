from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView

from sage_auth.mixins.email import EmailMixin
from sage_auth.utils import ActivationEmailSender, set_required_fields

class UserCreationMixin(CreateView, EmailMixin):
    """A mixin that handles user creation and login using a strategy-based form."""

    success_url = None
    form_class = None
    template_name = None
    email = None

    def form_valid(self, form):
        """Handle form validation, save the user, and log them in."""
        user = form.save()
        form.instance.id = user.id
        user.is_active = False
        user.save()

        if settings.SEND_OTP:
            self.email = self.send_otp_based_on_strategy(user)
            self.request.session["email"] = self.email
            self.request.session.save()

        elif settings.USER_ACCOUNT_ACTIVATION_ENABLED:
            user.is_active = False
            user.save()
            ActivationEmailSender().send_activation_email(user, self.request)
            messages.success(
                self.request,
                "Account created successfully. Please check your email to activate your account.",
            )
            return HttpResponse("Activation link sent to your email address")

        return redirect(self.get_success_url())

    def send_otp_based_on_strategy(self, user):
        """Send OTP based on the strategy in settings.AUTHENTICATION_METHODS."""
        username_field, _ = set_required_fields()

        if settings.AUTHENTICATION_METHODS.get("EMAIL_PASSWORD"):
            return EmailMixin.form_valid(self, user)

        if settings.AUTHENTICATION_METHODS.get("PHONE_PASSWORD"):
            self.send_otp_sms(user.phone_number)

        # if settings.AUTHENTICATION_METHODS.get('EMAIL_PASSWORD') and settings.AUTHENTICATION_METHODS.get('PHONE_PASSWORD'):
        #     EmailMixin.form_valid(self, form)
        #     self.send_otp_sms(user.phone_number)

    def send_otp_sms(self, phone_number):
        """Send OTP to the user's phone (Placeholder for SMS logic)."""
        pass

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """Return the success URL."""
        if not self.success_url:
            raise ValueError("The success_url attribute is not set.")
        return self.success_url

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("home")
        return super().get(request, *args, **kwargs)
