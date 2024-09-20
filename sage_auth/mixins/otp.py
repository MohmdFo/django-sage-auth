from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib import messages
from sage_auth.utils import send_email_otp,set_required_fields
from django.http import HttpResponse
from sage_auth.models import CustomUser

class EmailMixin:
    """Mixin to handle OTP generation and sending for email verification."""

    def generate_otp(self):
        """Generate a random OTP."""
        return get_random_string(length=6, allowed_chars='0123456789')

    def send_otp(self, email, otp):
        """Send OTP to the user's email."""
        send_email_otp(otp, email)

    def handle_otp(self, user_id):
        """Generate and send OTP if email is the USERNAME_FIELD."""
        username_field, _ = set_required_fields()
        if username_field == 'email':
            userObj = CustomUser.objects.get(id=user_id)

            otp = self.generate_otp()
            print(otp)
            self.send_otp(userObj.email, otp)

            userObj.is_active = True

            userObj.save()

            messages.info(self.request, f"Verification code was sent to your email: {userObj.email}")
            self.request.session['email'] = userObj.email  # Store email in session for verification

    def form_valid(self, form):
        """Handle OTP logic after the user is created."""
        user = form.instance.id

        self.handle_otp(user)
        return 
