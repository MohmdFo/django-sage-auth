from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm
from phonenumber_field.formfields import PhoneNumberField

from sage_auth.utils import set_required_fields
from sage_auth.models import SageUser

class PasswordResetFormMixin(forms.Form):
    """
    A mixin to handle password reset requests based on user-defined
    identifiers (email or phone number).

    The form dynamically selects
    the appropriate identifier field, either email or phone number,
    based on the configuration set in `settings`.
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
        identifier = PhoneNumberField(
            label=_(IDENTIFIER_FIELD_LABEL),
            region=getattr(settings, "DEFAULT_REGION", "IR"),
            widget=forms.TextInput(attrs={"placeholder": _("Phone Number")}),
        )
    else:
        identifier = forms.CharField(
            max_length=254,
            label=_(IDENTIFIER_FIELD_LABEL),
            widget=forms.TextInput(attrs={"placeholder": _(IDENTIFIER_FIELD_LABEL)}),
        )


class ResetPasswordConfirmsFormMixin(SetPasswordForm):
    """
    A custom form for resetting a user's password, extending Django's
    `SetPasswordForm` with additional styling for front-end integration.
    """

    class Meta:
        model = SageUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

