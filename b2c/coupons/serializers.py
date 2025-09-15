# b2c/coupons/serializers.py
from rest_framework import serializers
from .models import Coupon
from django.utils import timezone

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ["used_count"]

    def validate(self, data):
        if data["valid_from"] >= data["valid_until"]:
            raise serializers.ValidationError("`valid_from` must be before `valid_until`.")
        return data
