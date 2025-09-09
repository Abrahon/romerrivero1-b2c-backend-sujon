from django.db.models import TextChoices


class UserType(TextChoices):
    B2B = "b2b", "B2B User"
    B2C = "b2c", "B2C User"

class RoleChoices(TextChoices):
    ADMIN = 'admin', 'Admin'
    BUYER = 'buyer', 'Buyer'
 

    