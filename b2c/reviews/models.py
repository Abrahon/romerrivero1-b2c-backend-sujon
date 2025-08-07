from django.conf import settings
from django.db import models
from b2c.products.models import Products  

class Review(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    
    # Use the custom user model defined in settings.py
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}⭐"
