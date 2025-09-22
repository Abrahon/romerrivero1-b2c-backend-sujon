from rest_framework import serializers
from .models import Review
from decimal import Decimal

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.title", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "name",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "product", "user", "created_at"]

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        if value * 10 % 5 != 0:
            raise serializers.ValidationError("Rating must be in steps of 0.5 (e.g., 3.5, 4.0, 4.5).")
        return Decimal(value)
