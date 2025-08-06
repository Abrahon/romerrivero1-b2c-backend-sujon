from django.db import models
from accounts.models import User
from common.models import TimeStampedModel
from b2c.products.models import Products
from .enums import PaymentStatus
# Create your models here.


class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    is_paid = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"




class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"