from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import SageUser
from .utils import set_required_fields


class SageUserAdmin(UserAdmin):
    """Custom admin to display fields dynamically based on authentication strategy."""

    username_field, required_fields = set_required_fields()

    list_display = ["id", username_field] + required_fields + ["first_name", "last_name", "is_staff", "is_active"]

    fieldsets = (
        (None, {"fields": (username_field, "password")}),
        (_("Personal info"), {"fields": required_fields + ["first_name", "last_name"]}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "is_block",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (username_field, "password1", "password2")
                + tuple(required_fields),
            },
        ),
    )

    ordering = [username_field]


admin.site.register(SageUser, SageUserAdmin)
