from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from sage_auth.utils import set_required_fields
from sage_auth.manager.user import AuthUserManager
from sage_auth.helpers.validators import CompanyEmailValidator


class SageUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        validators=[CompanyEmailValidator()],
        help_text=_("Please provide a valid company email address."),
        db_comment="User's email address; must be unique and adhere to the company's email policy.",
        verbose_name=_("Email Address")
    )
    phone_number = PhoneNumberField(
        unique=True,
        null=True,
        blank=True,
        help_text=_("Enter a valid phone number, including country code."),
        db_comment="User's phone number; must be unique if provided.",
        verbose_name=_("Phone Number")
    )
    is_block = models.BooleanField(
        null=True,
        blank=True,
        help_text=_("Indicates whether the user is blocked."),
        db_comment="True if the user is blocked; null if the status is unknown.",
        verbose_name=_("Blocked Status")
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Optional username for the user, must be unique."),
        db_comment="Unique username for the user; primarily for legacy or specific application needs.",
        verbose_name=_("Username")
    )

    USERNAME_FIELD, REQUIRED_FIELDS = set_required_fields()

    objects: AuthUserManager = AuthUserManager()

    def __str__(self):
        if self.phone_number:
            return str(self.phone_number)
        return self.email

    def __repr__(self):
        return (
            f"<SageUser(username={self.username}, "
            f"email={self.email}, phone_number={self.phone_number})>"
        )

    class Meta:
        verbose_name = _("Sage User")
        verbose_name_plural = _("Sage Users")
        db_table = "sage_auth_user"
        db_table_comment = (
            "Stores user information including email, phone number, and block status. "
            "Extends the default Django AbstractUser model."
        )
