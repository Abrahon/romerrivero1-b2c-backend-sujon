# import re
# import json
# from rest_framework import serializers
# from cloudinary.uploader import upload
# from .models import Products, ProductCategory


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductCategory
#         fields = ["id", "name"]


# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
#     category_detail = CategorySerializer(source="category", read_only=True)
#     colors = serializers.ListField(
#         child=serializers.CharField(), required=True, allow_empty=True
#     )
#     images_upload = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )
#     discounted_price = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Products
#         fields = [
#             "id",
#             "title",
#             "product_code",
#             "category",
#             "category_detail",
#             "colors",
#             "available_stock",
#             "price",
#             "discount",
#             "discounted_price",
#             "description",
#             "images",
#             "images_upload",
#             "status",
#         ]
#         read_only_fields = ["id", "product_code", "images", "discounted_price"]

#     # ----------------------
#     # Helpers
#     # ----------------------
#     def _is_valid_hex(self, color):
#         return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color))

#     def _normalize_colors(self, colors):
#         if not colors:
#             return []
#         if isinstance(colors, str):
#             try:
#                 colors = json.loads(colors)
#             except json.JSONDecodeError:
#                 colors = [c.strip() for c in colors.split(",") if c.strip()]
#         normalized = []
#         for c in colors:
#             c = c.strip()
#             if not self._is_valid_hex(c):
#                 raise serializers.ValidationError(f"Invalid color code: {c}. Must be HEX like #RRGGBB.")
#             normalized.append(c.upper())
#         return normalized

#     # Validators

#     def validate_discount(self, value):
#         if value < 0 or value > 100:
#             raise serializers.ValidationError("Discount must be between 0 and 100.")
#         return value

#     def get_discounted_price(self, obj):
#         try:
#             return float(obj.price - (obj.price * obj.discount / 100)) if obj.discount > 0 else float(obj.price)
#         except Exception:
#             return float(obj.price)


#     # Images handling
 
#     def _upload_images(self, images):
#         """Upload list of images to Cloudinary and return URLs"""
#         urls = []
#         for image in images:
#             result = upload(image, folder="products")  # optional folder
#             url = result.get("secure_url")
#             if url:
#                 urls.append(url)
#         return urls

   
#     # Create / Update

#     def create(self, validated_data):
#         # Normalize colors
#         colors = self.initial_data.get("colors", [])
#         validated_data["colors"] = self._normalize_colors(colors)

#         # Pop uploaded images
#         images = validated_data.pop("images_upload", [])

#         # Create product
#         product = Products.objects.create(**validated_data)

#         # Upload images
#         if images:
#             product.images = self._upload_images(images)
#             product.save()

#         return product

#     def update(self, instance, validated_data):
#         # Normalize colors if provided
#         colors = self.initial_data.get("colors", None)
#         if colors is not None:
#             instance.colors = self._normalize_colors(colors)

#         # Handle new uploaded images
#         images = validated_data.pop("images_upload", None)
#         replace_images = self.initial_data.get("replace_images", False)  
#         if images:
#             uploaded_urls = self._upload_images(images)
#             if replace_images:
#                 instance.images = uploaded_urls
#             else:
#                 instance.images = (instance.images or []) + uploaded_urls

#         # Update other fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance
import re
import json
from rest_framework import serializers
from cloudinary.uploader import upload
from .models import Products, ProductCategory
from django.utils import timezone
import cloudinary.uploader


import cloudinary.uploader
from rest_framework import serializers
from .models import ProductCategory

import cloudinary.uploader
from rest_framework import serializers
from .models import ProductCategory

class CategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "icon","icon_url"]
    
    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.url
        return None

# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
#     category_detail = CategorySerializer(source="category", read_only=True)
#     colors = serializers.ListField(
#         child=serializers.CharField(), required=True, allow_empty=True
#     )
#     images_upload = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )
#     discounted_price = serializers.SerializerMethodField(read_only=True)
#     # main_images = ImagesField(null)
#     image = serializers.SerializerMethodField() 
#     average_rating = serializers.DecimalField(
#         max_digits=3, decimal_places=1, read_only=True
#     )
    
    
#     # -------------------------------
#     # Limited Deal Fields
#     # -------------------------------
#     limited_deal_price = serializers.DecimalField(
#         max_digits=10, decimal_places=2, required=False, allow_null=True
#     )
#     limited_deal_start = serializers.DateTimeField(required=False, allow_null=True)
#     limited_deal_end = serializers.DateTimeField(required=False, allow_null=True)

#     class Meta:
#         model = Products
#         fields = [
#             "id",
#             "title",
#             "product_code",
#             "category",
#             "category_detail",
#             "colors",
#             "available_stock",
#             "price",
#             "discount",
#             "discounted_price",
#             "description",
#             "images",
#             "images_upload",
#             "status",
#             "limited_deal_price",
#             "limited_deal_start",
#             "limited_deal_end",
#             "image",
#             "average_rating"
          
            
#         ]
#         read_only_fields = ["id", "product_code", "images", "discounted_price","product_name","average_rating"]
    
    
    
#     def get_image(self, obj):
#         try:
#             if obj.images and len(obj.images) > 0:
#                 return obj.images[0] 
#         except Exception:
#             return None
#         return None
#     # ----------------------
#     # Helpers
#     # ----------------------
#     def _is_valid_hex(self, color):
#         return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color))

#     def _normalize_colors(self, colors):
#         if not colors:
#             return []
#         if isinstance(colors, str):
#             try:
#                 colors = json.loads(colors)
#             except json.JSONDecodeError:
#                 colors = [c.strip() for c in colors.split(",") if c.strip()]
#         normalized = []
#         for c in colors:
#             c = c.strip()
#             if not self._is_valid_hex(c):
#                 raise serializers.ValidationError(f"Invalid color code: {c}. Must be HEX like #RRGGBB.")
#             normalized.append(c.upper())
#         return normalized

#     # Validators
#     def validate_discount(self, value):
#         if value < 0 or value > 100:
#             raise serializers.ValidationError("Discount must be between 0 and 100.")
#         return value

#     def validate(self, attrs):
#         # Validate limited deal fields
#         start = attrs.get("limited_deal_start")
#         end = attrs.get("limited_deal_end")
#         price = attrs.get("limited_deal_price")

#         if price is not None and (start is None or end is None):
#             raise serializers.ValidationError(
#                 "Limited deal price requires both start and end date."
#             )
#         if start and end and start >= end:
#             raise serializers.ValidationError(
#                 "Limited deal start must be before end date."
#             )
#         return attrs

#     def get_discounted_price(self, obj):
#         try:
#             now = timezone.now()
#             if obj.limited_deal_price and obj.limited_deal_start and obj.limited_deal_end:
#                 if obj.limited_deal_start <= now <= obj.limited_deal_end:
#                     return float(obj.limited_deal_price)
#             return float(obj.price - (obj.price * obj.discount / 100)) if obj.discount > 0 else float(obj.price)
#         except Exception:
#             return float(obj.price)

#     # ----------------------
#     # Images handling
#     # ----------------------
#     def _upload_images(self, images):
#         """Upload list of images to Cloudinary and return URLs"""
#         urls = []
#         for image in images:
#             result = upload(image, folder="products")
#             url = result.get("secure_url")
#             if url:
#                 urls.append(url)
#         return urls

#     # ----------------------
#     # Create / Update
#     # ----------------------
#     def create(self, validated_data):
#         # Normalize colors
#         colors = self.initial_data.get("colors", [])
#         validated_data["colors"] = self._normalize_colors(colors)

#         # Pop uploaded images
#         images = validated_data.pop("images_upload", [])

#         # Create product
#         product = Products.objects.create(**validated_data)

#         # Upload images
#         if images:
#             product.images = self._upload_images(images)
#             product.save()

#         return product

#     def update(self, instance, validated_data):
#         # Normalize colors if provided
#         colors = self.initial_data.get("colors", None)
#         if colors is not None:
#             instance.colors = self._normalize_colors(colors)

#         # Update other fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance

#         # Handle new uploaded images
#         images = validated_data.pop("images_upload", None)
#         replace_images = self.initial_data.get("replace_images", False)
#         if images:
#             uploaded_urls = self._upload_images(images)
#             if replace_images:
#                 instance.images = uploaded_urls
#             else:
#                 instance.images = (instance.images or []) + uploaded_urls

#         # Update limited deal fields
#     for field in ["limited_deal_price", "limited_deal_start", "limited_deal_end"]:
#             if field in validated_data:
#                 setattr(instance, field, validated_data.pop(field))

#         # Update other fields
#     for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance

import re
import json
from rest_framework import serializers
from cloudinary.uploader import upload
from .models import Products, ProductCategory
from django.utils import timezone

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    category_detail = CategorySerializer(source="category", read_only=True)
    colors = serializers.ListField(
        child=serializers.CharField(), required=True, allow_empty=True
    )
    images_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    images_delete = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False,
        help_text="List of image URLs to delete"
    )
    discounted_price = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    image = serializers.SerializerMethodField() 

    class Meta:
        model = Products
        fields = [
            "id", "title", "product_code", "category", "category_detail",
            "colors", "available_stock", "price", "discount", "discounted_price",
            "description", "images", "images_upload", "images_delete", "status",
            "limited_deal_price", "limited_deal_start", "limited_deal_end",
            "image", "average_rating"
        ]
        read_only_fields = ["id", "product_code", "images", "discounted_price", "average_rating"]
    
    def get_image(self, obj):
        try:
            if obj.images and len(obj.images) > 0:
                return obj.images[0] 
        except Exception:
            return None
        return None

    # ----------------------
    # Colors
    # ----------------------
    def validate_colors(self, value):
        if not value:
            return []
        

        # Handle stringified JSON arrays
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
            try:
                value = json.loads(value[0])
            except json.JSONDecodeError:
                value = [c.strip() for c in value[0].split(",") if c.strip()]

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = [c.strip() for c in value.split(",") if c.strip()]

        # Validate each HEX color
        normalized = []
        for c in value:
            c = c.strip().upper()
            if not re.match(r"^#(?:[0-9A-F]{3}){1,2}$", c):
                raise serializers.ValidationError(f"Invalid color code: {c}")
            normalized.append(c)
        return normalized

    # ----------------------
    # Create product
    # ----------------------

    def create(self, validated_data):
        images = validated_data.pop("images_upload", [])
        product = Products.objects.create(**validated_data)

        image_urls = []
        print(images)
        for image in images:
            try:
                result = upload(image)  # Upload to Cloudinary
                image_urls.append(result.get("secure_url"))
            except Exception as e:
                raise serializers.ValidationError({"images_upload": f"Image upload failed: {str(e)}"})

        if image_urls:
            product.images = image_urls  # Store list of URLs in JSONField
            product.save(update_fields=["images"])

        return product
    
    #  update color
    # def update(self, instance, validated_data):
    #     # Update colors if provided
    #     colors = validated_data.pop("colors", None)
    #     if colors is not None:
    #         instance.colors = colors  
            

    #     # Handle uploaded images
    #     images = validated_data.pop("images_upload", None)
    #     replace_images = self.initial_data.get("replace_images", False)
    #     if images:
    #         uploaded_urls = self._upload_images(images)
    #         if replace_images:
    #             instance.images = uploaded_urls
    #         else:
    #             instance.images = (instance.images or []) + uploaded_urls

    #     # Update other fields
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     instance.save()
    #     return instance


    def update(self, instance, validated_data):
    # ----------------------
    # Colors
    # ----------------------
        colors = validated_data.pop("colors", None)
        if colors is not None:
            instance.colors = colors

        # ----------------------
        # Images
        # ----------------------
        # Handle uploaded images
        images = validated_data.pop("images_upload", None)
        replace_images = self.initial_data.get("replace_images", False)
        delete_images = self.initial_data.get("delete_images", [])

        # Remove images if delete_images provided
        if delete_images:
            instance.images = [img for img in (instance.images or []) if img not in delete_images]

        # Add new uploaded images
        if images:
            uploaded_urls = self._upload_images(images)
            if replace_images:
                instance.images = uploaded_urls
            else:
                instance.images = (instance.images or []) + uploaded_urls

        # ----------------------
        # Update other fields
        # ----------------------
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



    # ----------------------
    # Images handling
    # ----------------------
    def _upload_images(self, images):
        urls = []
        for image in images:
            result = upload(image, folder="products")
            url = result.get("secure_url")
            if url:
                urls.append(url)
        return urls

    # ----------------------
    # Price / Discount
    # ----------------------
    def get_discounted_price(self, obj):
        now = timezone.now()
        if obj.limited_deal_price and obj.limited_deal_start and obj.limited_deal_end:
            if obj.limited_deal_start <= now <= obj.limited_deal_end:
                return float(obj.limited_deal_price)
        return float(obj.price - (obj.price * obj.discount / 100)) if obj.discount > 0 else float(obj.price)
