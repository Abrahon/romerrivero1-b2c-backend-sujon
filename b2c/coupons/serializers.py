# from rest_framework import serializers
# from .models import Coupon, CouponRedemption

# class CouponSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Coupon
#         fields = "__all__"
#         read_only_fields = ['id']

# class ApplyCouponSerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=50)
#     product_id = serializers.IntegerField(required=False)

#     def validate_code(self, value):
#         from django.utils import timezone
#         try:
#             coupon = Coupon.objects.get(code=value, active=True)
#         except Coupon.DoesNotExist:
#             raise serializers.ValidationError("Invalid or inactive coupon.")

#         now = timezone.now()
#         if not (coupon.valid_from <= now <= coupon.valid_to):
#             raise serializers.ValidationError("This coupon is expired or not active yet.")
#         return value
from rest_framework import serializers
from .models import Coupon, CouponRedemption

class CouponSerializer(serializers.ModelSerializer):
    description = serializers.CharField(
        required=True,         # ensures API input is mandatory
        allow_blank=False      # cannot be empty string
    )

    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ['id']

class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    product_id = serializers.IntegerField(required=False)

    def validate_code(self, value):
        from django.utils import timezone
        try:
            coupon = Coupon.objects.get(code=value, active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive coupon.")

        now = timezone.now()
        if not (coupon.valid_from <= now <= coupon.valid_to):
            raise serializers.ValidationError("This coupon is expired or not active yet.")
        return value
