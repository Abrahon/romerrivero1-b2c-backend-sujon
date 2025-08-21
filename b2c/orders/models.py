# b2c/orders/models.py
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
import secrets
from common .models import TimeStampedModel
from .enums import OrderStatus
from b2c.products.models import Products



class Order(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=255, unique=True, editable=False)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, default="pending")
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} — {self.user}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            ts = timezone.now().strftime("%Y%m%d%H%M%S")
            rnd = secrets.token_hex(3)
            self.order_number = f"ORD-{ts}-{rnd}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    # Import Products model according to  project
    
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def line_total(self):
        return (self.price_at_time or Decimal("0.00")) * self.quantity
