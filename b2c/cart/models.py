from django.db import models

from django.db import models
from django.conf import settings
from b2c.products.models import Products
from cloudinary.models import CloudinaryField

User = settings.AUTH_USER_MODEL

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # image = CloudinaryField("cart_image", blank=True, null=True)  
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user} - {self.product.title} ({self.quantity})"

