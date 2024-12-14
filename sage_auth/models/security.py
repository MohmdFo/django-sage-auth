from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Security(models.Model):
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
        db_comment="The user this security data belongs to."
    )
    total_logins = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of successful login attempts."),
        db_comment="Tracks the total number of successful login attempts for the user."
    )
    admin_logins = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of successful admin login attempts."),
        db_comment="Tracks the total number of successful admin login attempts for the user."
    )
    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text=_("Total number of failed login attempts."),
        db_comment="Tracks the total number of failed login attempts for the user."
    )

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
        return f"Security Metrics for {self.user}"

    class Meta:
        verbose_name = _("Security")
        verbose_name_plural = _("Security")
        indexes = [
            models.Index(fields=["user"], name="idx_security_user")
        ]
        db_table_comment = "Tracks security-related metrics such as login counts and failed attempts for users."
