from django.db import models


class ShippingStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'