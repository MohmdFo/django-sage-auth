from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import TemplateView, View
from sage_otp.helpers.choices import ReasonOptions

from sage_auth.forms import CustomUserCreationForm, PasswordResetForm
from sage_auth.mixins import (
    ForgetPasswordConfirmMixin,
    ForgetPasswordDoneMixin,
    ForgetPasswordMixin,
    ReactivationMixin,
    UserCreationMixin,
    VerifyOtpMixin,
)
from sage_auth.utils import set_required_fields

User = get_user_model()


class SignUpView(UserCreationMixin):
    form_class = CustomUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("verify")


class HomeV(LoginRequiredMixin, TemplateView):
    template_name = "home.html"


class OtpVerificationView(VerifyOtpMixin, TemplateView):
    success_url = reverse_lazy("home")
    """View to handle OTP verification."""

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        return super().setup(request, *args, **kwargs)

    template_name = "verify.html"
    success_url = reverse_lazy("home")

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ForgetPasswordView(ForgetPasswordMixin):
    template_name = "forget-password.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("auth-otp-verification")

    def get_success_url(self) -> str:
        """Return the success URL for OTP verification."""
        return reverse_lazy("auth-otp-verification")


class ForgetPasswordOTPConfirmView(ForgetPasswordConfirmMixin, TemplateView):
    template_name = "verify_email.html"
    success_url = reverse_lazy("auth-reset-password")
    reason = ReasonOptions.FORGET_PASSWORD

    def setup(self, request, *args, **kwargs):
        self.user_identifier = request.session.get("email")
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ForgetPasswordConfirmView(ForgetPasswordDoneMixin):
    template_name = "reset_password.html"
    success_url = reverse_lazy("login")


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"Decoded UID: {uid}")  # Debugging point
        user = User.objects.get(id=uid)
        if user is not None:
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Your account has been activated successfully. You can now log in.",
            )
            return redirect("login")
        else:
            messages.error(request, "The activation link is invalid or has expired.")
            return redirect("register")


class CustomLoginView(LoginView):
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
                return redirect(self.get_success_url())
            else:
                messages.error(
                    self.request,
                    "Your account is not activated. Please check your email for the activation link.",
                )
                self.request.session["email"] = identifier
                return redirect("reactivate")
        else:
            return super().form_invalid(form)


class ReactivateUserView(ReactivationMixin):
    success_url = reverse_lazy("home")
    template_name = "reactivate.html"
