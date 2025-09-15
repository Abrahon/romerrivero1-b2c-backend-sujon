from django.db import models
from django.conf import settings
from b2c.products.models import Products
from common.models import TimeStampedModel

User = settings.AUTH_USER_MODEL

class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="wishlist_items"
    )
    product = models.ForeignKey(
        Products, 
        on_delete=models.CASCADE, 
        related_name="wishlisted_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist items
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user} - {self.product.name}"
