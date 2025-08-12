from django.db import models


class IndustryTypeChoices(models.TextChoices):
    TECH = 'TECH', 'Technology'
    FINANCE = 'FINANCE', 'Finance'
    HEALTHCARE = 'HEALTHCARE', 'Healthcare'
    EDUCATION = 'EDUCATION', 'Education'
    RETAIL = 'RETAIL', 'Retail'
    MANUFACTURING = 'MANUFACTURING', 'Manufacturing'
    OTHER = 'OTHER', 'Other'
