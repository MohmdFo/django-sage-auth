from django import forms
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from sage_auth.helpers.validators import CompanyEmailValidator
from sage_auth.models import SageUser
from sage_auth.utils import set_required_fields


class SageUserFormMixin(forms.ModelForm):
    """
    A mixin that handles dynamic field generation and validation
    based on authentication strategies.

    This must be extended by the developer.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    )

    class Meta:
        model = SageUser
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        username_field, required_fields = set_required_fields()

        if username_field == "email":
            self.fields["email"] = forms.EmailField(
                required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"})
            )
            self.fields["email"].validators.append(CompanyEmailValidator())

        elif username_field == "phone_number":
            self.fields["phone_number"] = PhoneNumberField(
                region=getattr(settings, "DEFAULT_REGION", "IR"),
                required=True,
                widget=forms.TextInput(attrs={"placeholder": "Phone Number"}),
            )
        elif username_field == "username":
            self.fields["username"] = forms.CharField(
                required=True, widget=forms.TextInput(attrs={"placeholder": "Username"})
            )

        # Add any additional required fields based on strategies
        for field in required_fields:
            if field == "email" and "email" not in self.fields:
                self.fields["email"] = forms.EmailField(
                    required=True,
                    widget=forms.EmailInput(attrs={"placeholder": "Email"}),
                )
                self.fields["email"].validators.append(CompanyEmailValidator())

            if field == "username" and "username" not in self.fields:
                self.fields["username"] = forms.CharField(
                    required=True,
                    widget=forms.TextInput(attrs={"placeholder": "Username"}),
                )
            if field == "phone_number" and "phone_number" not in self.fields:
                self.fields["phone_number"] = PhoneNumberField(
                    region=getattr(settings, "DEFAULT_REGION", "CA"),
                    required=True,
                    widget=forms.TextInput(attrs={"placeholder": "Phone Number"}),
                )

        # Move password fields to the end
        self.fields["password1"] = self.fields.pop("password1")
        self.fields["password2"] = self.fields.pop("password2")

    def clean_password1(self):
        """Validate the password using Django's default password validators."""
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e) from e
        return password

    def clean(self):
        """Validate that the required fields have been filled correctly and passwords
        match.
        """
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        username = cleaned_data.get("username")

        # Ensure that at least one identifier is provided
        if not email and not phone_number and not username:
            raise forms.ValidationError(
                "You must provide at least one identifier: email, phone number, or username."
            )

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")

        return cleaned_data

    def get_user_data(self):
        """Extract and return user data from cleaned_data."""
        return {
            "email": self.cleaned_data.get("email"),
            "phone_number": self.cleaned_data.get("phone_number"),
            "username": self.cleaned_data.get("username"),
            "password": self.cleaned_data.get("password1"),
        }

    def save(self, commit=True):
        """Save the custom user using the dynamic strategy."""
        user_data = self.get_user_data()

        # Determine the strategy using your custom UserManager logic
        strategy = SageUser.objects.get_authentication_strategies(user_data)
        user = strategy.create_user(user_data)

        return user


class SageUserCreationForm(SageUserFormMixin):
    """Custom form for user creation that extends the SageUserFormMixin."""

    def __init__(self, *args, **kwargs):
        """Customize the form fields, attributes, and validators."""
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({"placeholder": "Enter the pass"})
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm the pass"}
        )


class PasswordResetFormMixin(forms.Form):
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


class OtpLoginFormMixin(forms.Form):
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


class PasswordResetForm(PasswordResetFormMixin):
    def __init__(self, *args, **kwargs):
        """Customize the form fields, attributes, and validators."""
        super().__init__(*args, **kwargs)


class ResetPasswordConfrimForm(SetPasswordForm):
    class Meta:
        model = SageUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
