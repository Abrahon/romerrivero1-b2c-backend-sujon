import uuid
import json
from django.utils.text import slugify
from django.core.files.storage import default_storage
from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_detail = CategorySerializer(source='category', read_only=True)
    colors = serializers.ListField(child=serializers.CharField(), required=False)
    images_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'product_code', 'category', 'category_detail',
            'colors', 'available_stock', 'price', 'description',
            'images', 'images_upload', 'status',
        ]
        read_only_fields = ['id', 'product_code', 'images']

    def _normalize_colors(self, colors):
        """Normalize colors input into a list of strings."""
        if not colors:
            return []
        if isinstance(colors, str):
            try:
                return json.loads(colors)  # handles JSON string
            except json.JSONDecodeError:
                return [c.strip() for c in colors.split(",") if c.strip()]  # handles comma-separated
        if isinstance(colors, list):
            return colors
        return []

    def create(self, validated_data):
        # Handle colors
        colors = self.initial_data.get("colors", [])
        validated_data["colors"] = self._normalize_colors(colors)

        # Handle images
        images = validated_data.pop("images_upload", [])
        product = Product.objects.create(**validated_data)

        image_paths = []
        for image in images:
            ext = image.name.split(".")[-1]
            seo_name = f"{slugify(product.title)}-{uuid.uuid4().hex}.{ext}"
            full_path = f"product_images/{seo_name}"
            saved_path = default_storage.save(full_path, image)
            image_paths.append(saved_path)

        product.images = image_paths
        product.save()

        return product

    def update(self, instance, validated_data):
        # Handle colors
        colors = validated_data.pop("colors", None)
        if colors is not None:
            instance.colors = self._normalize_colors(colors)

        # Handle images
        images = validated_data.pop("images_upload", [])
        if images:
            image_paths = []
            for image in images:
                ext = image.name.split(".")[-1]
                seo_name = f"{slugify(instance.title)}-{uuid.uuid4().hex}.{ext}"
                full_path = f"product_images/{seo_name}"
                saved_path = default_storage.save(full_path, image)
                image_paths.append(saved_path)
            instance.images = image_paths

        return super().update(instance, validated_data)
