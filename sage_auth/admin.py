from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from sage_auth.models import LoginAttempt, SageUser, SecurityAnnouncement

from .utils import set_required_fields


@admin.register(SageUser)
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


@admin.register(LoginAttempt)
class LoginAttemptModelAdmin(admin.ModelAdmin):
    """Admin interface for managing LoginAttempt Model entries."""

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        latest_attempts = (
            qs.values("user")
            .annotate(latest_id=Max("id"))
            .values_list("latest_id", flat=True)
        )
        return qs.filter(id__in=latest_attempts)


@admin.register(SecurityAnnouncement)
class SecurityAnnouncementAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SecurityAnnouncement model.

    Provides a user-friendly interface with search, filtering, inline editing,
    and fieldsets for better management of security announcements.
    """

    # Display fields in the admin list view
    list_display = (
        "title",
        "group",
        "is_active",
        "date",
        "location",  # Fields to display in the list view
    )
    # Fields that can be used to search records
    search_fields = (
        "title",
        "subtitle",
        "content",
        "location",  # Allows text-based search
    )
    # Filters in the sidebar for quick record categorization
    list_filter = (
        "is_active",
        "group",
        "date",  # Boolean, choice, and date filters
    )
    # Fields to make editable directly in the list view
    list_editable = (
        "is_active",
        "group",  # Allows quick activation/deactivation and group assignment
    )
    # Ordering of records
    ordering = ("-date", "title")  # Sorts records by descending date and then title
    # Prepopulated fields
    prepopulated_fields = {
        "subtitle": ("title",)
    }  # Automatically generate subtitles from titles (optional)
    # Fieldsets for organizing the form view
    fieldsets = (
        ("General Information", {"fields": ("title", "subtitle", "content", "group")}),
        ("Status and Visibility", {"fields": ("is_active", "date", "location")}),
        (
            "Call-to-Action Button",
            {
                "fields": ("button_text", "button_link"),
                "classes": ("collapse",),  # Collapsed by default
            },
        ),
    )
    # Read-only fields
    readonly_fields = ("date",)  # Example: Prevent editing of date field (optional)

    # Decorated custom actions
    @admin.action(description="Mark selected announcements as active")
    def mark_active(self, request, queryset):
        """Custom action to mark selected announcements as active."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated} announcement(s) successfully marked as active."
        )

    @admin.action(description="Mark selected announcements as inactive")
    def mark_inactive(self, request, queryset):
        """Custom action to mark selected announcements as inactive."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} announcement(s) successfully marked as inactive."
        )

    # Registering the actions
    actions = [mark_active, mark_inactive]
