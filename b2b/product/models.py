# b2c/products/models.py
from django.db import models
import uuid
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Product Model: Represents the wholesale products available for sale in the B2B system.
class Product(models.Model):
    title = models.CharField(max_length=255)
    product_code = models.CharField(max_length=255, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    color = models.CharField(max_length=50)
    available_stock = models.PositiveIntegerField()  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    description = models.TextField() 
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  

    # New fields added for B2B
    # bulk_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  
    # minimum_order_quantity = models.PositiveIntegerField(default=1)

    # Auto-generate product code on save
    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = str(uuid.uuid4()).split('-')[0] 
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title



