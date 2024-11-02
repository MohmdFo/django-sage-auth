from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .base import AuthStrategy


class EmailStrategy(AuthStrategy):
    """
    Strategy for creating and handling user account using email authentication.

    This strategy allows for creating and configuring a user account based on
    email, password, and additional fields such as `is_staff` and
    `is_superuser`.
    It follows the general structure of Django's `get_user_model()` to create
    and customize the user model with email as the primary identifier.
    """

    def validate(self, user_data):
        email = user_data.get("email")
        if not email:
            raise ValidationError("Email is required.")

    def create_user(self, user_data, user=None):
        """Create a user using the email field."""
        if user is None:
            User = get_user_model()
            user = User()

        user.email = user_data["email"]
        user.is_staff = user_data.get("is_staff", False)
        user.is_superuser = user_data.get("is_superuser", False)
        password = user_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        return user
