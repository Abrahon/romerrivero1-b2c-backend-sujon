# b2c/coupons/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=(("percent", "Percent"), ("fixed", "Fixed Amount")),
        default="percent"
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    usage_limit = models.PositiveIntegerField(default=1)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)  # total uses allowed
    used_count = models.PositiveIntegerField(default=0)   # how many times used
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self, order_total: Decimal) -> bool:
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            self.used_count < self.usage_limit and
            order_total >= self.min_order_amount
        )
