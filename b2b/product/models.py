from django.db import models
import uuid

class Product(models.Model):
    title = models.CharField(max_length=255)
    product_code = models.CharField(max_length=255, unique=True, editable=False)
    category = models.CharField(max_length=255)  
    color = models.CharField(max_length=50)
    available_stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # optional image

    # Auto-generate product code on save
    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = str(uuid.uuid4()).split('-')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
