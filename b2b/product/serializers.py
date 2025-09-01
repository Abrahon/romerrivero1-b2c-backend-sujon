from rest_framework import serializers
from .models import Product
from .models import Product, Category
from django.utils.text import slugify
import uuid
from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     images_upload = serializers.ListField(
#         child=serializers.ImageField(),
#         write_only=True,
#         required=False
#     )

#     class Meta:
#         model = Product
#         fields = ['id', 'title', 'product_code', 'category', 'color', 'available_stock', 'price', 'description', 'images', 'images_upload']
#         read_only_fields = ['id', 'product_code', 'images']

#     def create(self, validated_data):
#         images = validated_data.pop('images_upload', [])
#         product = Product.objects.create(**validated_data)

#         image_paths = []
#         for image in images:
#             ext = image.name.split('.')[-1]
#             seo_name = f"{slugify(product.title)}-{uuid.uuid4().hex}.{ext}"
#             full_path = f'product_images/{seo_name}'
#             with open(f'media/{full_path}', 'wb+') as f:
#                 for chunk in image.chunks():
#                     f.write(chunk)
#             image_paths.append(full_path)
#         product.images = image_paths
#         product.save()
#         return product



class ProductSerializer(serializers.ModelSerializer):
    # Use name of the category instead of PK
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    
    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'product_code', 'category', 'color', 'available_stock',
            'price', 'description', 'images', 'images_upload'
        ]
        read_only_fields = ['id', 'product_code', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images_upload', [])
        product = Product.objects.create(**validated_data)

        image_paths = []
        for image in images:
            ext = image.name.split('.')[-1]
            seo_name = f"{slugify(product.title)}-{uuid.uuid4().hex}.{ext}"
            full_path = f'product_images/{seo_name}'
            with open(f'media/{full_path}', 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_paths.append(full_path)

        product.images = image_paths
        product.save()
        return product
