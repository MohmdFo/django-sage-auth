# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

from sage_auth.helpers.validators import CompanyEmailValidator, validate_phone_number
from sage_auth.manager.user import AuthUserManager
from sage_auth.utils import set_required_fields


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True, null=True, blank=True, validators=[CompanyEmailValidator()]
    )
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_phone_number],
    )
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)

    USERNAME_FIELD, REQUIRED_FIELDS = set_required_fields()

    objects = AuthUserManager()

    def __str__(self):
        return self.USERNAME_FIELD
