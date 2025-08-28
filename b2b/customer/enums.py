from django.db.models import TextChoices

class CustomerStatus(TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'
