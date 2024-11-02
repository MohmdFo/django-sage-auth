# validators.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator as DjangoEmailValidator
from django.utils.translation import gettext_lazy as _


class CompanyEmailValidator(DjangoEmailValidator):
    """
    A custom email validator that extends Django's built-in EmailValidator.

    This validator checks if an email address is valid and, optionally, if it
    belongs to an approved domain defined in the Django settings. It ensures
    that the email format is correct and restricts users to
    email domains specified.
    in the `COMPANY_EMAIL_DOMAINS` setting, if provided.
    """

    def __call__(self, value):
        """Call the validation logic."""
        # First, call the original email validation
        super().__call__(value)

        # Check if COMPANY_EMAIL_DOMAINS is defined in settings
        company_email_domains = getattr(settings, "COMPANY_EMAIL_DOMAINS", None)

        # If company domains are defined, validate the domain
        if company_email_domains:
            email_domain = value.split("@")[-1]
            if not any(
                email_domain.endswith(domain) for domain in company_email_domains
            ):
                raise ValidationError(
                    _(
                        f'The email domain must be one of the following: {", ".join(company_email_domains)}'
                    )
                )
