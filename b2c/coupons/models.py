
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from b2c.products.models import Products,ProductCategory 
from .enums import DiscountType


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    # ✅ allow multiple
    products = models.ManyToManyField(Products, blank=True)
    categories = models.ManyToManyField(ProductCategory, blank=True)

    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.discount_value})"



class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="redemptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.coupon.code}"
