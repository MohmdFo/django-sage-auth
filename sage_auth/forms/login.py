from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from sage_auth.utils import set_required_fields

class OtpLoginFormMixin(forms.Form):
    """
    A form mixin for OTP-based login, supporting dynamic identifier fields
    (either email or phone number) based on the specified authentication.

    method in settings.
    """

    username_field, required_fields = set_required_fields()
    IDENTIFIER_FIELD_LABEL = None
    if username_field == "email" or username_field == "phone_number":
        IDENTIFIER_FIELD_LABEL = username_field

    else:
        for field in required_fields:
            if field == "email":
                IDENTIFIER_FIELD_LABEL = "Email"
                break
            elif field == "phone_number":
                IDENTIFIER_FIELD_LABEL = "PhoneNumber"

    if IDENTIFIER_FIELD_LABEL == "Phone Number":
        login_field = PhoneNumberField(
            label=_(IDENTIFIER_FIELD_LABEL),
            region=getattr(settings, "DEFAULT_REGION", "IR"),
            widget=forms.TextInput(attrs={"placeholder": _("Phone Number")}),
        )

    login_field = forms.CharField(
        max_length=254,
        label=_(IDENTIFIER_FIELD_LABEL),
        widget=forms.TextInput(attrs={"placeholder": _(IDENTIFIER_FIELD_LABEL)}),
    )
