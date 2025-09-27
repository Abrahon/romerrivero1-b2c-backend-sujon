# from rest_framework import serializers
# from django.utils import timezone
# from .models import Coupon, CouponRedemption
# from b2c.products.models import Products
# # b2c/coupons/serializers.py
# from rest_framework import serializers
# from django.utils import timezone
# from decimal import Decimal
# from .models import Coupon
# from b2c.products.models import Products

# class CouponSerializer(serializers.ModelSerializer):
#     description = serializers.CharField(required=True, allow_blank=False)

#     class Meta:
#         model = Coupon
#         fields = "__all__"
#         read_only_fields = ['id']



# class ApplyCouponSerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=50)
#     product_id = serializers.IntegerField(required=False)

#     def validate_code(self, value):
#         """
#         Ensure the coupon exists, is active, and is within valid dates.
#         """
#         try:
#             coupon = Coupon.objects.get(code=value, active=True)
#         except Coupon.DoesNotExist:
#             raise serializers.ValidationError("Invalid or inactive coupon.")

#         now = timezone.now()
#         valid_from = coupon.valid_from
#         valid_to = coupon.valid_to
#         if timezone.is_naive(valid_from):
#             valid_from = timezone.make_aware(valid_from)
#         if timezone.is_naive(valid_to):
#             valid_to = timezone.make_aware(valid_to)

#         if not (valid_from <= now <= valid_to):
#             raise serializers.ValidationError(
#                 f"This coupon is expired or not active yet. Valid from {valid_from} to {valid_to} UTC"
#             )

#         # Attach coupon instance to serializer for later use
#         self.context['coupon_instance'] = coupon
#         return value

#     def validate(self, attrs):
#         """
#         Ensure coupon applies to product or category correctly
#         """
#         coupon = self.context.get('coupon_instance')
#         product_id = attrs.get('product_id')

#         if not product_id:
#             raise serializers.ValidationError("Product ID is required.")

#         # Product-specific coupon
#         if coupon.product and coupon.product.id != product_id:
#             raise serializers.ValidationError("This coupon is not valid for this product.")

#         # Category-specific coupon
#         if coupon.category:
#             try:
#                 product = Products.objects.get(id=product_id)
#             except Products.DoesNotExist:
#                 raise serializers.ValidationError("Product does not exist.")

#             if product.category != coupon.category:
#                 raise serializers.ValidationError("This coupon is not valid for this category.")

#         # Add coupon instance to validated data
#         attrs['coupon'] = coupon
#         return attrs

from rest_framework import serializers
from django.utils import timezone
from .models import Coupon, CouponRedemption, Products, ProductCategory
from .enums import DiscountType

class CouponSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Products.objects.all(), required=False
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ProductCategory.objects.all(), required=False
    )

    class Meta:
        model = Coupon
        fields = '__all__'

    def validate(self, attrs):
        products = attrs.get('products', [])
        categories = attrs.get('categories', [])

        # ✅ Must select at least one
        if not products and not categories:
            raise serializers.ValidationError(
                {"non_field_errors": ["At least one product or category must be selected."]}
            )

        # ✅ Extra check for percentage coupons
        if attrs['discount_type'] == DiscountType.PERCENTAGE and attrs['discount_value'] > 100:
            raise serializers.ValidationError(
                {"discount_value": "Percentage discount cannot exceed 100%."}
            )

        return attrs

    def create(self, validated_data):
        products = validated_data.pop('products', [])
        categories = validated_data.pop('categories', [])

        coupon = Coupon.objects.create(**validated_data)

        if products:
            coupon.products.set(products)
        if categories:
            coupon.categories.set(categories)

        return coupon

    def update(self, instance, validated_data):
        products = validated_data.pop('products', None)
        categories = validated_data.pop('categories', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if products is not None:
            instance.products.set(products)
        if categories is not None:
            instance.categories.set(categories)

        return instance



# class ApplyCouponSerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=50)
#     product_id = serializers.IntegerField(required=False)

#     def validate_code(self, value):
#         try:
#             coupon = Coupon.objects.get(code=value, active=True)
#         except Coupon.DoesNotExist:
#             raise serializers.ValidationError("Invalid or inactive coupon.")
#         now = timezone.now()
#         if not (coupon.valid_from <= now <= coupon.valid_to):
#             raise serializers.ValidationError(
#                 f"Coupon not valid now. Valid from {coupon.valid_from} to {coupon.valid_to} UTC"
#             )
#         self.context['coupon_instance'] = coupon
#         return value

#     def validate(self, attrs):
#         coupon = self.context.get('coupon_instance')
#         product_id = attrs.get('product_id')

#         # If product_id provided, validate against coupon
#         if product_id:
#             try:
#                 product = Products.objects.get(id=product_id)
#             except Products.DoesNotExist:
#                 raise serializers.ValidationError("Product does not exist.")

#             # Check if product belongs to coupon
#             if coupon.products.exists() and product not in coupon.products.all():
#                 raise serializers.ValidationError("Coupon not valid for this product.")

#             # Check category
#             if coupon.categories.exists() and product.category not in coupon.categories.all():
#                 raise serializers.ValidationError("Coupon not valid for this category.")

#         attrs['coupon'] = coupon
#         return attrs
from rest_framework import serializers
from django.utils import timezone
from .models import Coupon, Products

class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()
    product_ids = serializers.ListField(
        child=serializers.IntegerField(), required=True
    )

    def validate(self, attrs):
        code = attrs.get("code")
        product_ids = attrs.get("product_ids")

        # Check coupon existence
        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid or inactive coupon."})

        # Expiry check
        now = timezone.now()
        if coupon.valid_from and coupon.valid_from > now:
            raise serializers.ValidationError({"code": "Coupon is not yet valid."})
        if coupon.valid_to and coupon.valid_to < now:
            raise serializers.ValidationError({"code": "Coupon has expired."})

        # Product validation
        if not product_ids or len(product_ids) == 0:
            raise serializers.ValidationError({"product_ids": "At least one product ID is required."})

        products = Products.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise serializers.ValidationError({"product_ids": "One or more product IDs are invalid."})

        # Restriction checks (if coupon is tied to products/categories)
        if coupon.products.exists():
            allowed_ids = set(coupon.products.values_list("id", flat=True))
            for pid in product_ids:
                if pid not in allowed_ids:
                    raise serializers.ValidationError({
                        "product_ids": f"Your selected product coupon is invalide {pid}."
                    })

        if coupon.categories.exists():
            allowed_cats = set(coupon.categories.values_list("id", flat=True))
            for product in products:
                if product.category_id not in allowed_cats:
                    raise serializers.ValidationError({
                        "product_ids": f"Coupon not valid for category of product {product.id}."
                    })

        attrs["coupon"] = coupon
        attrs["products"] = products
        return attrs
