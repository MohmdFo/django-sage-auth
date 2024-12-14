from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from sage_auth.models import SageUser, Security

from .utils import set_required_fields


class SageUserAdmin(UserAdmin):
    """Custom admin to display fields dynamically based on authentication strategy."""

    username_field, required_fields = set_required_fields()

    list_display = (
        ["id", username_field]
        + required_fields
        + ["first_name", "last_name", "is_staff", "is_active"]
    )

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
                    "is_block" "user_permissions",
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


class SecurityModelAdmin(admin.ModelAdmin):
    """Admin interface for managing SecurityModel entries."""

    list_display = ["user", "total_logins", "admin_logins", "failed_attempts"]
    search_fields = ["user__username", "user__email", "user__phone_number"]
    list_filter = ["user__is_staff", "user__is_superuser"]

    readonly_fields = ["total_logins", "admin_logins", "failed_attempts"]

    fieldsets = (
        (None, {"fields": ("user",)}),
        (
            _("Login Metrics"),
            {
                "fields": (
                    "total_logins",
                    "admin_logins",
                    "failed_attempts",
                )
            },
        ),
    )


admin.site.register(SageUser, SageUserAdmin)
admin.site.register(Security, SecurityModelAdmin)
