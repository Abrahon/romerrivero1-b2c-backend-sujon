from django.db.models import TextChoices

class RoleChoices(TextChoices):
    ADMIN = 'admin', 'Admin'
    BUYER = 'buyer', 'Buyer'
    