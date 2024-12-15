from django.db import models
from django.utils.translation import gettext_lazy as _

class GroupChoices(models.TextChoices):
    ALERT = 'ALERT', _("Alert")
    GUIDELINE = 'GUIDELINE', _("Guideline")
