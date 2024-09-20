from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.conf import settings

from sage_auth.mixins.otp import EmailMixin
from sage_auth.forms import CustomUserCreationForm
from sage_auth.utils import set_required_fields

class UserCreationMixin(CreateView,EmailMixin):
    """A mixin that handles user creation and login using a strategy-based form."""
    
    success_url = None  # Define this in the views that inherit the mixin
    form_class = None   # Define the form class in the views
    template_name = None  # Define the template to use in the views

    def form_valid(self, form):
        """Handle form validation, save the user, and log them in."""
        user = form.save()
        form.instance.id = user.id
        if settings.SEND_OTP:
            self.send_otp_based_on_strategy(user,form)

        login(self.request, user)
        return redirect(self.get_success_url())

    def send_otp_based_on_strategy(self, user,form):
        """Send OTP based on the strategy in settings.AUTHENTICATION_METHODS."""
        username_field, _ = set_required_fields()

        if settings.AUTHENTICATION_METHODS.get('EMAIL_PASSWORD'):
            EmailMixin.form_valid(self, form)

        if settings.AUTHENTICATION_METHODS.get('PHONE_PASSWORD'):
            self.send_otp_sms(user.phone_number)

        if settings.AUTHENTICATION_METHODS.get('EMAIL_PASSWORD') and settings.AUTHENTICATION_METHODS.get('PHONE_PASSWORD'):
            EmailMixin.form_valid(self, form)
            self.send_otp_sms(user.phone_number)

    def send_otp_sms(self, phone_number):
        """Send OTP to the user's phone (Placeholder for SMS logic)."""
        # Placeholder for now, implement SMS logic here
        pass

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """Return the success URL."""
        if not self.success_url:
            raise ValueError("The success_url attribute is not set.")
        return self.success_url

class SignUpView(UserCreationMixin):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('home')

class HomeV(LoginRequiredMixin,TemplateView):
    template_name = 'home.html'