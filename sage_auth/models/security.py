from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from sage_tools.mixins.models import TimeStampMixin

from sage_auth.helpers.choices import GroupChoices
from sage_auth.repository import LoginAttemptManager


class LoginAttempt(TimeStampMixin):
    """
    A model to track security-related metrics for a user.

    Fields:
        user: ForeignKey to the user model, representing the user associated with the security metrics.
        total_logins: Integer tracking the total successful login attempts.
        admin_logins: Integer tracking the total successful admin login attempts.
        failed_attempts: Integer tracking the total failed login attempts.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security",
        help_text=_("The user associated with this security entry."),
        db_comment="The user this security data belongs to.",
    )
    total_logins = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of successful login attempts."),
        db_comment="Tracks the total number of successful login attempts for the user.",
    )
    admin_logins = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of successful admin login attempts."),
        db_comment="Tracks the total number of successful admin login attempts for the user.",
    )
    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of failed login attempts."),
        db_comment="Tracks the total number of failed login attempts for the user.",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of the last login attempt.",
        db_comment="Tracks the timestamp of the most recent login attempt.",
    )
    objects = LoginAttemptManager()

    def increment_total_logins(self):
        """Increments the total logins by 1."""
        self.total_logins += 1
        self.save()

    def increment_admin_logins(self):
        """Increments the admin logins by 1."""
        self.admin_logins += 1
        self.save()

    def increment_failed_attempts(self):
        """Increments the failed login attempts by 1."""
        self.failed_attempts += 1
        self.save()

    def reset_failed_attempts(self):
        """Resets the failed login attempts to 0."""
        self.failed_attempts = 0
        self.save()

    def __str__(self):
        return f"Login Attempt Metrics for {self.user}"

    class Meta:
        verbose_name = _("Login Attempt")
        verbose_name_plural = _("Login Attempt")
        indexes = [models.Index(fields=["user"], name="idx_security_user")]
        db_table_comment = "Tracks security-related metrics such as login counts and failed attempts for users."


class SecurityAnnouncement(TimeStampMixin):
    """
    Model representing a security announcement or alert for users,
    containing details such as title, content, date, and optional call-to-action.

    buttons.

    Designed to assist administrators in managing announcements while providing metadata for developers.
    """

    title = models.CharField(
        max_length=255,
        help_text=_(
            "Enter the main title of the announcement (e.g., 'Security Guidelines')."
        ),
        db_comment="The main title of the security announcement.",
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_(
            "Optional subtitle providing additional context (e.g., 'Login Attempt Failed')."
        ),
        db_comment="An optional subtitle for the announcement.",
    )
    content = models.TextField(
        help_text=_(
            "Add the main content of the announcement, explaining details to users."
        ),
        db_comment="The detailed text content of the security announcement.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Mark this as active to display it to users or inactive to hide it."
        ),
        db_comment="Indicates whether the security announcement is active or inactive.",
    )
    group = models.CharField(
        max_length=10,
        choices=GroupChoices.choices,
        default=GroupChoices.ALERT,
        help_text=_("Specify whether this is an alert or a guideline."),
        db_comment="Categorizes the announcement as either an alert or a guideline.",
    )
    button_text = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_(
            "Enter text for the call-to-action button (e.g., 'Join' or 'Register')."
        ),
        db_comment="The label for the call-to-action button, if applicable.",
    )
    button_link = models.URLField(
        blank=True,
        null=True,
        help_text=_("Provide the URL the button redirects to, if applicable."),
        db_comment="The URL linked to the call-to-action button.",
    )
    date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Specify the date of the announcement or event."),
        db_comment="The date associated with the security announcement.",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_(
            "Enter the location for the event, if applicable (e.g., 'Soho Avenue, Tokyo')."
        ),
        db_comment="Optional location details for the announcement.",
    )

    def __str__(self):
        return f"{self.title} ({self.date})" if self.date else self.title

    class Meta:
        verbose_name = _("Security Announcement")
        verbose_name_plural = _("Security Announcements")
