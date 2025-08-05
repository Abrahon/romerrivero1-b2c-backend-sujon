from common.models import TimeStampedModel 
from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=255)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

        
class Products(TimeStampedModel):
    category = models.ForeignKey(Category,  related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rating = models.FloatField(default=0.0)  
    tags = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title




