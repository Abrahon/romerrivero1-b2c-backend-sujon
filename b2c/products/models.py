import uuid
import os
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField  # optional, if needed
from common.models import TimeStampedModel
from .enums import ProductStatus


# -------------------------------
# Product Category Model
# -------------------------------
class ProductCategory(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# -------------------------------
# Helper function for image path
# -------------------------------
def product_image_path(instance, filename):
    base, ext = os.path.splitext(filename)
    slug = slugify(instance.title)
    return f'product_images/{slug}-{uuid.uuid4().hex}{ext}'


# -------------------------------
# Product Model
# -------------------------------
class Products(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    product_code = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        default='TEMP'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    colors = models.JSONField(default=list)
    available_stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage (0-100)"
    )
    description = models.TextField()
    images = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.INACTIVE
    )

    # -------------------------------
    # Auto-generate product_code if TEMP
    # -------------------------------
    def save(self, *args, **kwargs):
        if not self.product_code or self.product_code == 'TEMP':
            self.product_code = str(uuid.uuid4()).split('-')[0]
        super().save(*args, **kwargs)

    # -------------------------------
    # Calculate discounted price
    # -------------------------------
    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    def __str__(self):
        return self.title
