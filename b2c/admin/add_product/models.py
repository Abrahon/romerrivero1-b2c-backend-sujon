# b2c/products/models.py
from django.db import models
import uuid
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    product_code = models.CharField(max_length=255, unique=True, editable=False)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    color = models.CharField(max_length=50)
    available_stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = str(uuid.uuid4()).split('-')[0]  # Generate product code
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="wishlist"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name="wishlisted_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # Prevent duplicate wishlist entries
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} -> {self.product}"
