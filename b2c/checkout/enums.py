from django.db import models


class ShippingStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SHIPPED = 'SHIPPED', 'Shipped'
    SUCCESS = "SUCCESS", "Payment Successful"
    DELIVERED = 'DELIVERED', 'Delivered'



