import re
import uuid
import json
from django.utils.text import slugify
from rest_framework import serializers
from cloudinary.uploader import upload
from .models import Products, ProductCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    category_detail = CategorySerializer(source="category", read_only=True)
    colors = serializers.ListField(
        child=serializers.CharField(), required=True, allow_empty=True
    )
    images_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    discounted_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Products
        fields = [
            "id",
            "title",
            "product_code",
            "category",
            "category_detail",
            "colors",
            "available_stock",
            "price",
            "discount",
            "discounted_price",
            "description",
            "images",
            "images_upload",
            "status",
        ]
        read_only_fields = ["id", "product_code", "images", "discounted_price"]

    # -------------------------------
    # HEX color validation
    # -------------------------------
    def _is_valid_hex(self, color):
        hex_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
        return bool(hex_pattern.match(color))

    def _normalize_colors(self, colors):
        if not colors:
            return []

        if isinstance(colors, str):
            try:
                colors = json.loads(colors)
            except json.JSONDecodeError:
                colors = [c.strip() for c in colors.split(",") if c.strip()]

        normalized = []
        for c in colors:
            c = c.strip()
            if not self._is_valid_hex(c):
                raise serializers.ValidationError(
                    f"Invalid color code: {c}. Must be HEX like #RRGGBB."
                )
            normalized.append(c.upper())

        return normalized

    # -------------------------------
    # Discount validation
    # -------------------------------
    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value

    def get_discounted_price(self, obj):
        """Calculate price after discount"""
        if obj.discount > 0:
            return float(obj.price - (obj.price * obj.discount / 100))
        return float(obj.price)

    # -------------------------------
    # Create Product
    # -------------------------------
    def create(self, validated_data):
        colors = self.initial_data.get("colors", [])
        validated_data["colors"] = self._normalize_colors(colors)

        images = validated_data.pop("images_upload", [])
        product = Products.objects.create(**validated_data)

        # Upload images to Cloudinary
        image_urls = []
        for image in images:
            result = upload(image)
            image_urls.append(result['secure_url'])

        product.images = image_urls
        product.save()
        return product

    # -------------------------------
    # Update Product
    # -------------------------------
    def update(self, instance, validated_data):
        colors = self.initial_data.get("colors", None)
        if colors is not None:
            instance.colors = self._normalize_colors(colors)

        images = validated_data.pop("images_upload", [])
        if images:
            image_urls = instance.images or []
            for image in images:
                result = upload(image)
                image_urls.append(result['secure_url'])
            instance.images = image_urls

        # Update other fields dynamically
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
