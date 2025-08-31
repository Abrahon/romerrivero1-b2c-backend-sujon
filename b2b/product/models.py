from django.db import models
import uuid
import os
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


def product_image_path(instance, filename):
    base, ext = os.path.splitext(filename)
    slug = slugify(instance.title)
    return f'product_images/{slug}-{uuid.uuid4().hex}{ext}'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    product_code = models.CharField(max_length=255, unique=True, editable=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')  
    color = models.CharField(max_length=50)
    available_stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    # Store multiple images in JSON
    images = models.JSONField(default=list, blank=True)  

    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = str(uuid.uuid4()).split('-')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
