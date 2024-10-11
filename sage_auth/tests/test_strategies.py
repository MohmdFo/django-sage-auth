# tests/test_strategies.py
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from sage_auth.strategies.email_strategy import EmailStrategy
from sage_auth.strategies.phone_strategy import PhoneStrategy
from sage_auth.strategies.username_strategy import UsernameStrategy
from sage_auth.strategies.combined_strategy import CombinedStrategy

User = get_user_model()

@pytest.mark.django_db
class TestEmailStrategy:
    """Test cases for EmailStrategy."""

    def test_validate_valid_email(self):
        """Test that a valid email passes validation."""
        strategy = EmailStrategy()
        user_data = {"email": "test@example.com"}
        strategy.validate(user_data)  # Should not raise an exception

    def test_create_user_with_email(self):
        """Test that a user is created successfully with a valid email."""
        strategy = EmailStrategy()
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "is_staff": True,
            "is_superuser": False
        }
        user = strategy.create_user(user_data)
        assert user.email == "newuser@example.com"
        assert user.is_staff
        assert not user.is_superuser
        assert user.check_password("testpassword123")


@pytest.mark.django_db
class TestPhoneStrategy:
    """Test cases for PhoneStrategy."""

    def test_validate_valid_phone(self):
        """Test that a valid phone number passes validation."""
        strategy = PhoneStrategy()
        user_data = {"phone_number": "+12345678901"}
        strategy.validate(user_data)  # Should not raise an exception

    def test_validate_invalid_phone(self):
        """Test that an invalid phone number raises a ValidationError."""
        strategy = PhoneStrategy()
        user_data = {"phone_number": "invalid-phone"}
        with pytest.raises(ValidationError, match="Invalid phone number format."):
            strategy.validate(user_data)

    def test_validate_existing_phone(self):
        """Test that an existing phone number raises a ValidationError."""
        strategy = PhoneStrategy()
        User.objects.create(phone_number="+12345678901")
        user_data = {"phone_number": "+12345678901"}
        with pytest.raises(ValidationError, match="Phone number already exists."):
            strategy.validate(user_data)

    def test_create_user_with_phone(self):
        """Test that a user is created successfully with a valid phone number."""
        strategy = PhoneStrategy()
        user_data = {
            "phone_number": "+9876543210",
            "password": "testpassword123",
            "is_staff": True,
            "is_superuser": False
        }
        user = strategy.create_user(user_data)
        assert user.phone_number == "+9876543210"
        assert user.is_staff
        assert not user.is_superuser
        assert user.check_password("testpassword123")


@pytest.mark.django_db
class TestUsernameStrategy:
    """Test cases for UsernameStrategy."""

    def test_validate_valid_username(self):
        """Test that a valid username passes validation."""
        strategy = UsernameStrategy()
        user_data = {"username": "newuser"}
        strategy.validate(user_data)  # Should not raise an exception

    def test_validate_existing_username(self):
        """Test that an existing username raises a ValidationError."""
        strategy = UsernameStrategy()
        User.objects.create(username="existinguser")
        user_data = {"username": "existinguser"}
        with pytest.raises(ValidationError, match="Username already exists."):
            strategy.validate(user_data)

    def test_create_user_with_username(self):
        """Test that a user is created successfully with a valid username."""
        strategy = UsernameStrategy()
        user_data = {
            "username": "newuser",
            "password": "testpassword123",
            "is_staff": True,
            "is_superuser": False
        }
        user = strategy.create_user(user_data)
        assert user.username == "newuser"
        assert user.check_password("testpassword123")


@pytest.mark.django_db
class TestCombinedStrategy:
    """Test cases for CombinedStrategy."""

    def test_create_user_with_multiple_strategies(self):
        """Test that a user is created successfully with multiple strategies."""
        strategies = [EmailStrategy(), PhoneStrategy(), UsernameStrategy()]
        combined_strategy = CombinedStrategy(strategies)
        user_data = {
            "email": "user@example.com",
            "phone_number": "+1234567890",
            "username": "multiuser",
            "password": "testpassword123",
            "is_staff": True,
            "is_superuser": False
        }
        user = combined_strategy.create_user(user_data)
        assert user.email == "user@example.com"
        assert user.phone_number == "+1234567890"
        assert user.username == "multiuser"
        assert user.is_staff
        assert not user.is_superuser
        assert user.check_password("testpassword123")
