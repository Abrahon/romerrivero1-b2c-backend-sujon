from django.conf import settings
from django.db import models
from b2c.products.models import Products
from common.models import TimeStampedModel


class Review(TimeStampedModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)  
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.title} - {self.rating}⭐"
