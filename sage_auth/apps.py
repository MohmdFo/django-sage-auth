from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SageAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sage_auth"
    verbose_name = _("SAGE Auth")

    def ready(self):
        import sage_auth.checks
