# urls.py
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    ActivateAccountView,
    CustomLoginView,
    ForgetPasswordConfirmView,
    ForgetPasswordOTPConfirmView,
    ForgetPasswordView,
    HomeV,
    OtpVerificationView,
    ReactivateUserView,
    SignUpView,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(template_name="login.html"), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("home/", HomeV.as_view(), name="home"),
    path("verify/", OtpVerificationView.as_view(), name="verify"),
    path("forgot-password/", ForgetPasswordView.as_view(), name="auth-forgot-password"),
    path(
        "forgot-password/verify-otp/",
        ForgetPasswordOTPConfirmView.as_view(),
        name="auth-otp-verification",
    ),
    path(
        "reset-password/",
        ForgetPasswordConfirmView.as_view(),
        name="auth-reset-password",
    ),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),
    path("reactivate/", ReactivateUserView.as_view(), name="reactivate"),
]
