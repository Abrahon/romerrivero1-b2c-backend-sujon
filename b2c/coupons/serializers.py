
from rest_framework import serializers
from django.utils import timezone
from .models import Coupon, CouponRedemption
from b2c.products.models import Products

class CouponSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ['id']


# b2c/coupons/serializers.py
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import Coupon
from b2c.products.models import Products

class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    product_id = serializers.IntegerField(required=False)

    def validate_code(self, value):
        """
        Ensure the coupon exists, is active, and is within valid dates.
        """
        try:
            coupon = Coupon.objects.get(code=value, active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive coupon.")

        now = timezone.now()
        valid_from = coupon.valid_from
        valid_to = coupon.valid_to
        if timezone.is_naive(valid_from):
            valid_from = timezone.make_aware(valid_from)
        if timezone.is_naive(valid_to):
            valid_to = timezone.make_aware(valid_to)

        if not (valid_from <= now <= valid_to):
            raise serializers.ValidationError(
                f"This coupon is expired or not active yet. Valid from {valid_from} to {valid_to} UTC"
            )

        # Attach coupon instance to serializer for later use
        self.context['coupon_instance'] = coupon
        return value

    def validate(self, attrs):
        """
        Ensure coupon applies to product or category correctly
        """
        coupon = self.context.get('coupon_instance')
        product_id = attrs.get('product_id')

        if not product_id:
            raise serializers.ValidationError("Product ID is required.")

        # Product-specific coupon
        if coupon.product and coupon.product.id != product_id:
            raise serializers.ValidationError("This coupon is not valid for this product.")

        # Category-specific coupon
        if coupon.category:
            try:
                product = Products.objects.get(id=product_id)
            except Products.DoesNotExist:
                raise serializers.ValidationError("Product does not exist.")

            if product.category != coupon.category:
                raise serializers.ValidationError("This coupon is not valid for this category.")

        # Add coupon instance to validated data
        attrs['coupon'] = coupon
        return attrs
