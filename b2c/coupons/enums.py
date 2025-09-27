from django.utils.translation import gettext_lazy as _
from django.db import models

class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', _('Percentage')
    FIXED = 'fixed', _('Fixed Amount')
