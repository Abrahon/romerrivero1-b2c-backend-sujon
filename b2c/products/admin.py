from django.contrib import admin

# Register your models here.
from .models import ProductCategory, Products

admin.site.register(ProductCategory)
admin.site.register(Products)



