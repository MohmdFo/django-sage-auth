from django.conf import settings
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string

def otpCreate():
    number = random.randint(10000,99999)
    return str(number)

def send_email_otp(token,email):

    subject = 'Email Verification'
    message = render_to_string('email_verification_template.html',
                               {'verification_code': token})
    from_email = 'martinwatson20227@gmail.com'
    recipient_list = [email]

    send_mail(subject,
              '',
              from_email,
              recipient_list,
              html_message=message,
              fail_silently=False)

def set_required_fields():
    """Dynamically set the USERNAME_FIELD and REQUIRED_FIELDS based on settings."""
    
    # Initialize the username_field and required_fields list
    username_field = None
    required_fields = []

    # Iterate over the settings in the order defined in AUTHENTICATION_METHODS
    for method in settings.AUTHENTICATION_METHODS:
        if settings.AUTHENTICATION_METHODS[method]:
            # Set the first enabled method as the username_field
            if username_field is None:
                if method == 'EMAIL_PASSWORD':
                    username_field = 'email'
                elif method == 'PHONE_PASSWORD':
                    username_field = 'phone_number'
                elif method == 'USERNAME_PASSWORD':
                    username_field = 'username'
            else:
                # Add remaining enabled fields to required_fields
                if method == 'EMAIL_PASSWORD':
                    required_fields.append('email')
                elif method == 'PHONE_PASSWORD':
                    required_fields.append('phone_number')
                elif method == 'USERNAME_PASSWORD':
                    required_fields.append('username')

    # Ensure no duplicates in required_fields
    required_fields = list(set(required_fields))

    return username_field, required_fields
