from django.contrib import admin
from .models import Category, Product

# --------------------------
# Category Admin
# --------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


# --------------------------
# Product Admin
# --------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_code', 'category', 'available_stock', 'price', 'status')
    list_filter = ('status', 'category')
    search_fields = ('title', 'product_code', 'description')
    ordering = ('title',)
    readonly_fields = ('product_code',)  # prevent editing automatically generated product_code

    # Optional: show images in admin
    def image_preview(self, obj):
        if obj.images:
            return f'<img src="{obj.images[0]}" width="100" />'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

    # Optional: show JSON fields nicely
    def colors_list(self, obj):
        return ", ".join(obj.colors)
    colors_list.short_description = 'Colors'
