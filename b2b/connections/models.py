from django.db import models
from common.models import TimeStampedModel
from .enums import CompanyCategory, ConnectionCategory

# Create your models here.

class Connection(TimeStampedModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='connections/images/', default='default_image.png')
    company_category = models.CharField(
        max_length=20,
        choices=CompanyCategory.choices,  
        default=CompanyCategory.IT 
    )
    connection_category = models.CharField(
        max_length=20,
        choices=ConnectionCategory.choices, 
        default=ConnectionCategory.PARTNER 
    )
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



