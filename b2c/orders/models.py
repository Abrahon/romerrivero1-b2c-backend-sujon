
# b2c/orders/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import secrets
from common.models import TimeStampedModel
from .enums import OrderStatus, PaymentMethodChoices,PaymentStatus
from b2c.coupons.models import Coupon
from datetime import timedelta

class Order(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.COD)
    order_number = models.CharField(max_length=255, unique=True, editable=False)
    shipping_address = models.ForeignKey("checkout.Shipping", on_delete=models.SET_NULL, null=True, related_name='orders')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discounted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_paid = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
  
#   order number genarete
    def __str__(self):
        return f"{self.order_number} — {self.user}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            ts = timezone.now().strftime("%Y%m%d%H%M%S")
            rnd = secrets.token_hex(3)
            self.order_number = f"ORD-{ts}-{rnd}"
        super().save(*args, **kwargs)
        

        # Set estimated delivery for paid orders or COD
        if not self.estimated_delivery and (self.is_paid or self.payment_method == "COD"):
            self.estimated_delivery = timezone.now() + timedelta(days=5)
            super().save(update_fields=["estimated_delivery"])
        
        # if not self.estimated_delivery and (self.is_paid or self.payment_method == "COD"):
        #     self.estimated_delivery = timezone.now() + timedelta(days=5)
        #     super().save(update_fields=["estimated_delivery"])


    
    # calculate total ammount 
    def calculate_totals(self):
        """Recalculate totals from items + coupon"""
        subtotal = sum(item.line_total for item in self.items.all())
        self.total_amount = subtotal

        if self.coupon:
            discount = (subtotal * self.coupon.discount_percentage) / Decimal("100.0")
            self.discount_amount = discount
            self.final_amount = subtotal - discount
        else:
            self.discount_amount = Decimal("0.00")
            self.final_amount = subtotal
        return self.final_amount

    

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


# order tracking
class OrderTracking(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tracking_history'
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices 
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_updates'
    )
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order.order_number} - {self.status}"


