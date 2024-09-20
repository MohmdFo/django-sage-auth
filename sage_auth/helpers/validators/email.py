# validators.py

from django.core.validators import EmailValidator as DjangoEmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CompanyEmailValidator(DjangoEmailValidator):
    """
    Custom email validator that extends Django's EmailValidator.
    It validates the email format and optionally checks if the email domain is in the company-approved domains.
    """

    def __call__(self, value):
        """Call the validation logic."""
        # First, call the original email validation
        super().__call__(value)

        # Check if COMPANY_EMAIL_DOMAINS is defined in settings
        company_email_domains = getattr(settings, 'COMPANY_EMAIL_DOMAINS', None)

        # If company domains are defined, validate the domain
        if company_email_domains:
            email_domain = value.split('@')[-1]
            if not any(email_domain.endswith(domain) for domain in company_email_domains):
                raise ValidationError(
                    _(f'The email domain must be one of the following: {", ".join(company_email_domains)}')
                )
