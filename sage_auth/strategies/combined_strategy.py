# sage_auth/strategies/combined_strategy.py

from django.contrib.auth import get_user_model

from sage_auth.strategies.email_strategy import EmailStrategy
from sage_auth.strategies.phone_strategy import PhoneStrategy
from sage_auth.strategies.username_strategy import UsernameStrategy

from .base import AuthStrategy


class CombinedStrategy(AuthStrategy):
    """
    A strategy class to authenticate and create users using a combination of
    different authentication methods (email, phone, username, etc.).

    This class accepts multiple strategies, allowing for flexible user
    authentication based on defined strategies (e.g., EmailStrategy,
    PhoneStrategy, UsernameStrategy). It validates user data and creates user
    objects with attributes from each provided strategy.
    """

    def __init__(self, strategies):
        """Initialize with multiple strategies."""
        self.strategies = strategies

    def validate(self, user_data):
        """Validate user data with all strategies."""
        for strategy in self.strategies:
            strategy.validate(user_data)

    def create_user(self, user_data):
        """Create a user using data from all strategies."""
        User = get_user_model()

        # Create base user object
        user = User()

        # Set fields from each strategy
        for strategy in self.strategies:
            if isinstance(strategy, EmailStrategy) and "email" in user_data:
                user.email = user_data["email"]
            if isinstance(strategy, PhoneStrategy) and "phone_number" in user_data:
                user.phone_number = user_data["phone_number"]
            if isinstance(strategy, UsernameStrategy) and "username" in user_data:
                user.username = user_data["username"]

        # Set the password
        user.is_staff = user_data.get("is_staff", False)
        user.is_superuser = user_data.get("is_superuser", False)
        password = user_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        return user
