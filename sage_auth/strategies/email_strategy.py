from django.contrib.auth import get_user_model

from .base import AuthStrategy


class EmailStrategy(AuthStrategy):
    def validate(self, user_data):
        # email = user_data.get('email')
        # if not email:
        #     raise ValidationError("Email is required.")
        # try:
        #     validate_email(email)
        # except ValidationError:
        #     raise ValidationError("Invalid email format.")
        # if get_user_model().objects.filter(email=email).exists():
        #     raise ValidationError("Email already exists.")
        pass

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
        print("User created")
        return user
