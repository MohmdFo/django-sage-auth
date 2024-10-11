import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ValidatorE164:
    """Custom phone number validator supporting multiple formats."""

    message = _(
        "Invalid phone number format. Must be one of the following: 09xxxxxxxxx, +98xxxxxxxxx, or 0098xxxxxxxxx."
    )
    code = "invalid"

    # Regex pattern to support:
    # 1. Local format starting with 09
    # 2. International format with +98
    # 3. International format with 00 and country code
    regex = re.compile(r"^(?:\+98|00?98|0)?9\d{9}$")

    def __init__(self, message=None, code=None):
        """Initializes the ValidatorE164 with optional custom message and code.

        Args:
            message (str, optional): Custom error message.
            code (str, optional): Custom error code.
        """
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """Validates that the provided value matches the accepted phone number formats.

        Args:
            value (str): The phone number to validate.

        Raises:
            ValidationError: If the value does not match the accepted formats.
        """
        if not self.regex.match(value):
            raise ValidationError(self.message, code=self.code, params={"value": value})

    def __eq__(self, other):
        """Compares this ValidatorE164 instance with another for equality.

        Args:
            other (ValidatorE164): Another instance to compare with.

        Returns:
            bool: True if both instances have the same message and code, False otherwise.
        """
        return (
            isinstance(other, ValidatorE164)
            and self.message == other.message
            and self.code == other.code
        )


validate_phone_number = ValidatorE164()
