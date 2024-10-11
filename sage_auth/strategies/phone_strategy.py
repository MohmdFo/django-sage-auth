import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .base import AuthStrategy


class PhoneStrategy(AuthStrategy):
    def validate(self, user_data):
        phone_number = user_data.get("phone_number")
        if not phone_number:
            raise ValidationError("Phone number is required.")

        if not re.match(r"^\+?\d{10,15}$", phone_number):
            raise ValidationError("Invalid phone number format.")
        if get_user_model().objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number already exists.")

    def create_user(self, user_data, user=None):
        """Create a user using the phone number field."""
        if user is None:
            User = get_user_model()
            user = User()

        user.phone_number = user_data["phone_number"]
        user.is_staff = user_data.get("is_staff", False)
        user.is_superuser = user_data.get("is_superuser", False)
        password = user_data.get("password")
        if password:
            user.set_password(password)
        user.save()
        return user
