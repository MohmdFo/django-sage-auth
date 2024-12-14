from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from sage_auth.helpers.validators import CompanyEmailValidator
from sage_auth.manager.user import AuthUserManager
from sage_auth.utils import set_required_fields


class SageUser(AbstractUser):
    email = models.EmailField(
        unique=True, null=True, blank=True, validators=[CompanyEmailValidator()]
    )
    phone_number = PhoneNumberField(
        unique=True,
        null=True,
        blank=True,
    )
    is_block = models.BooleanField(null=True, blank=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)

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
        verbose_name = "Sage User"
        verbose_name_plural = "Sage Users"
