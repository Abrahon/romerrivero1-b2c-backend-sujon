
import uuid
import os
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from common.models import TimeStampedModel,TimeStampe
from .enums import ProductStatus
from cloudinary.models import CloudinaryField 


class ProductCategory(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    icon = CloudinaryField("category_icons", blank=True, null=True)

    def __str__(self):
        return self.name


# -------------------------------
# Helper function for product image path
# -------------------------------
def product_image_path(instance, filename):
    base, ext = os.path.splitext(filename)
    slug = slugify(instance.title)
    return f'product_images/{slug}-{uuid.uuid4().hex}{ext}'


# -------------------------------
# Product Model
# -------------------------------
class Products(TimeStampedModel):
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
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    # -------------------------------
    # Limited Deal Fields
    # -------------------------------
    limited_deal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Price during the limited deal"
    )
    limited_deal_start = models.DateTimeField(blank=True, null=True)
    limited_deal_end = models.DateTimeField(blank=True, null=True)
    limited_deal = models.BooleanField(default=False) 
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
        """
        Returns the discounted price or limited deal price if active.
        """
        now = timezone.now()
        if self.limited_deal_price and self.limited_deal_start and self.limited_deal_end:
            if self.limited_deal_start <= now <= self.limited_deal_end:
                return self.limited_deal_price

        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    def __str__(self):
        return self.title
