from django.db import models


class IndustryTypeChoices(models.TextChoices):
    SOFTWARE = 'Software industry', 'Software industry'
    HARDWARE = 'Hardware industry', 'Hardware industry'
    FINANCE = 'Finance industry', 'Finance industry'
    OTHER = 'Other', 'Other'

