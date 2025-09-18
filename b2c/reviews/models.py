from django.conf import settings
from django.db import models
from b2c.products.models import Products
from common.models import TimeStampedModel

class Review(TimeStampedModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    # Use the custom user model defined in settings.py
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()  
    comment = models.TextField(blank=True)  

    def __str__(self):
        return f"{self.user.email} - {self.product.name} - {self.rating}⭐"
