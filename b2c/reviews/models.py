from django.db import models
from django.contrib.auth.models import User
from b2c.products.models import Products 
from common .models import TimeStampedModel


# Create your models here.
class models(TimeStampedModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

