import re
import json
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

    # ----------------------
    # Helpers
    # ----------------------
    def _is_valid_hex(self, color):
        return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color))

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
                raise serializers.ValidationError(f"Invalid color code: {c}. Must be HEX like #RRGGBB.")
            normalized.append(c.upper())
        return normalized

    # ----------------------
    # Validators
    # ----------------------
    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value

    def get_discounted_price(self, obj):
        try:
            return float(obj.price - (obj.price * obj.discount / 100)) if obj.discount > 0 else float(obj.price)
        except Exception:
            return float(obj.price)

    # ----------------------
    # Images handling
    # ----------------------
    def _upload_images(self, images):
        """Upload list of images to Cloudinary and return URLs"""
        urls = []
        for image in images:
            result = upload(image, folder="products")  # optional folder
            url = result.get("secure_url")
            if url:
                urls.append(url)
        return urls

    # ----------------------
    # Create / Update
    # ----------------------
    def create(self, validated_data):
        # Normalize colors
        colors = self.initial_data.get("colors", [])
        validated_data["colors"] = self._normalize_colors(colors)

        # Pop uploaded images
        images = validated_data.pop("images_upload", [])

        # Create product
        product = Products.objects.create(**validated_data)

        # Upload images
        if images:
            product.images = self._upload_images(images)
            product.save()

        return product

    def update(self, instance, validated_data):
        # Normalize colors if provided
        colors = self.initial_data.get("colors", None)
        if colors is not None:
            instance.colors = self._normalize_colors(colors)

        # Handle new uploaded images
        images = validated_data.pop("images_upload", None)
        replace_images = self.initial_data.get("replace_images", False)  
        if images:
            uploaded_urls = self._upload_images(images)
            if replace_images:
                instance.images = uploaded_urls
            else:
                instance.images = (instance.images or []) + uploaded_urls

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
