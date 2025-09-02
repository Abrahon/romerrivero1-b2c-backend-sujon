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
    # Instead of PK, allow UID
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()  
    )
   

    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'product_code', 'category', 'category_detail',
            'colors', 'available_stock', 'price', 'description',
            'images', 'images_upload'
        ]
        read_only_fields = ['id', 'product_code', 'images']

    def create(self, validated_data):
        # Get raw colors
        colors = self.initial_data.get('colors', [])
        print("Initial colors data:", colors)

        # Parse colors
        if isinstance(colors, str):
            try:
                colors = json.loads(colors)
            except json.JSONDecodeError:
                colors = [color.strip() for color in colors.split(',') if color.strip()]
        if not colors:

           colors = []
        validated_data['colors'] = colors

        # Handle category by UID
        category_uid = validated_data.pop('category')
        try:
            category = Category.objects.get(id=category_uid)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category": "Invalid category UID"})
        validated_data['category'] = category

        # Handle images
        images = validated_data.pop('images_upload', [])
        product = Product.objects.create(**validated_data)

        image_paths = []
        for image in images:
            ext = image.name.split('.')[-1]
            seo_name = f"{slugify(product.title)}-{uuid.uuid4().hex}.{ext}"
            full_path = f'product_images/{seo_name}'
            saved_path = default_storage.save(full_path, image)
            image_paths.append(saved_path)

        product.images = image_paths
        product.save()
        return product
