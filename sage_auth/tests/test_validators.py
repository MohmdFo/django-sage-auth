# sage_auth/tests/test_validators.py

import pytest
from django.core.exceptions import ValidationError
from django.conf import settings
from sage_auth.helpers.validators import CompanyEmailValidator


class TestCompanyEmailValidator:
    """Test the CompanyEmailValidator."""

    @pytest.fixture(autouse=True)
    def setup(self, settings):
        """Set up company email domains for testing."""
        settings.COMPANY_EMAIL_DOMAINS = ["example.com", "company.org"]

    def test_valid_email_with_correct_domain(self):
        """Test valid email with an allowed company domain."""
        validator = CompanyEmailValidator()

        # This should not raise any exception
        validator("user@example.com")
        validator("employee@company.org")

    def test_invalid_email_format(self):
        """Test invalid email format."""
        validator = CompanyEmailValidator()

        # Invalid email format should raise ValidationError
        with pytest.raises(ValidationError):
            validator("invalid-email-format")

    def test_valid_email_with_incorrect_domain(self):
        """Test valid email format with a domain not in the allowed company domains."""
        validator = CompanyEmailValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator("user@otherdomain.com")

        assert "The email domain must be one of the following" in str(exc_info.value)

    def test_no_company_email_domains_set(self, settings):
        settings.COMPANY_EMAIL_DOMAINS = None
        validator = CompanyEmailValidator()

        validator("user@anydomain.com")
