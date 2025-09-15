# b2c/checkout/models.py
from django.db import models
from accounts.models import User
from common.models import TimeStampedModel
from .enums import ShippingStatusChoices  # Import the choices
from b2c.orders.models import Order


class Shipping(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping')
    full_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    email = models.EmailField()
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100)
    floor = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)
    
    # Make the field nullable if it can be null initially
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shippings', null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=ShippingStatusChoices.choices,
        default=ShippingStatusChoices.PENDING
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"
