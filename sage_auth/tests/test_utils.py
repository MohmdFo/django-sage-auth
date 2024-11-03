# sage_auth/tests/test_utils.py

import pytest
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from sage_auth.utils import (
    send_email_otp,
    set_required_fields,
    ActivationEmailSender,
    get_backends
)

User = get_user_model()


class TestUtils:
    """Test class for utility functions."""

    @pytest.mark.django_db
    def test_send_email_otp(self):
        """Test sending an email OTP."""
        token = "12345"
        email = "test@example.com"

        send_email_otp(token, email)

        # Test that one message has been sent
        assert len(mail.outbox) == 1
        # Test that the subject is correct
        assert mail.outbox[0].subject == "Email Verification"
        assert mail.outbox[0].to == [email]
        assert mail.outbox[0].body is not None

    @pytest.mark.parametrize(
        "auth_methods, expected_username, expected_required_fields",
        [
            ({"EMAIL_PASSWORD": True}, "email", []),
            ({"PHONE_PASSWORD": True}, "phone_number", []),
            ({"USERNAME_PASSWORD": True}, "username", []),
            (
                {"EMAIL_PASSWORD": True, "PHONE_PASSWORD": True},
                "email",
                ["phone_number"],
            ),
            (
                {"EMAIL_PASSWORD": True, "USERNAME_PASSWORD": True},
                "email",
                ["username"],
            ),
        ],
    )
    def test_set_required_fields(self, auth_methods, expected_username, expected_required_fields):
        """Test that the set_required_fields function correctly identifies the username
        field and required fields.
        """
        settings.AUTHENTICATION_METHODS = auth_methods

        username_field, required_fields = set_required_fields()

        assert username_field == expected_username
        assert sorted(required_fields) == sorted(expected_required_fields)

    # @pytest.mark.django_db
    # def test_account_activation_token(self):
    #     """Test generating and validating an account activation token."""
    #     user = User.objects.create_user(
    #         username="testuser", email="test@example.com", password="password123"
    #     )
    #     token = account_activation_token.make_token(user)

    #     # assert account_activation_token.check_token(user, token)
    #     # user.is_active = True
    #     # user.save()

    
    @pytest.mark.django_db
    def test_get_backends(self):
        """Test the get_backends function with real SMS backend."""
        sms_provider = get_backends()
        assert sms_provider is not None, "SMS provider should not be None"
        recipient_number = "+1234567890" 
        message_content = "This is a test message for get_backends function."

        result = sms_provider.send_one_message(recipient_number, message_content)
        assert result == None

