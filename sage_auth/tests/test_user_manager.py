from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAuthUserManager:
    """Test class for the AuthUserManager."""

    @pytest.mark.django_db
    @patch("builtins.input", side_effect=["test@example.com", "password123"])
    def test_create_user_with_email(self, mock_input):
        """Test creating a user with email strategy."""
        user_data = {"email": "test@example.com", "password": "password123"}

        user_manager = User.objects
        user = user_manager.create_user(**user_data)

        assert user.email == "test@example.com"
        assert user.check_password("password123")

    @pytest.mark.django_db
    @patch("builtins.input", side_effect=["+1234567890", "password123"])
    def test_create_user_with_phone(self, mock_input):
        """Test creating a user with phone strategy."""
        user_data = {"phone_number": "+1234567890", "password": "password123"}

        user_manager = User.objects
        user = user_manager.create_user(**user_data)

        assert user.phone_number == "+1234567890"
        assert user.check_password("password123")

    @pytest.mark.django_db
    @patch("builtins.input", side_effect=["username123", "password123"])
    def test_create_user_with_username(self, mock_input):
        """Test creating a user with username strategy."""
        user_data = {"username": "username123", "password": "password123"}

        user_manager = User.objects
        user = user_manager.create_user(**user_data)

        assert user.check_password("password123")

    @pytest.mark.django_db
    @patch("builtins.input", side_effect=["superuser@example.com", "superpassword123"])
    def test_create_superuser(self, mock_input):
        """Test creating a superuser."""
        user_data = {"email": "superuser@example.com", "password": "superpassword123"}

        user_manager = User.objects
        user = user_manager.create_superuser(**user_data)

        assert user.email == "superuser@example.com"
        assert user.check_password("superpassword123")
        assert user.is_staff
        assert user.is_superuser
