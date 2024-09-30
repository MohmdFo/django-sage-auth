# urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import SignUpView,HomeV,OtpVerificationView

urlpatterns = [
    # Django's built-in LoginView
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', SignUpView.as_view(),name='signup'),
    # Django's built-in LogoutView
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', HomeV.as_view(), name='home'),
    path('verify/',OtpVerificationView.as_view(), name='verify'),
]
