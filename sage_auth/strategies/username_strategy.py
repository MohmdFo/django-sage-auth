from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .base import AuthStrategy


class UsernameStrategy(AuthStrategy):
    def validate(self, user_data):
        username = user_data.get("username")
        if not username:
            raise ValidationError("Username is required.")
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")

    def create_user(self, user_data, user=None):
        """Create a user using the username field."""
        if user is None:
            User = get_user_model()
            user = User()

        user.username = user_data["username"]
        password = user_data.get("password")
        if password:
            user.set_password(password)
        user.save()
        return user
