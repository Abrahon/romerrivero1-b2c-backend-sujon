
# b2c/orders/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import secrets
from common.models import TimeStampedModel
from .enums import OrderStatus, PaymentMethodChoices

class Order(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.COD)
    order_number = models.CharField(max_length=255, unique=True, editable=False)
    shipping_address = models.ForeignKey("checkout.Shipping", on_delete=models.SET_NULL, null=True, related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discounted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, default="pending")
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number} — {self.user}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            ts = timezone.now().strftime("%Y%m%d%H%M%S")
            rnd = secrets.token_hex(3)
            self.order_number = f"ORD-{ts}-{rnd}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey("orders.Order", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("products.Products", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    @property
    def line_total(self):
        return (self.price or Decimal("0.00")) * self.quantity


class OrderTracking(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_updates')
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order.order_number} - {self.status}"
