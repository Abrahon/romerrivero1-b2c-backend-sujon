from rest_framework import serializers
from .models import Review
from decimal import Decimal

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.title", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)
    user_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "name",
            "rating",
            "user_image",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "product", "user", "name", "user_image", "created_at"]

    def get_user_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile.image and request:
            return request.build_absolute_uri(obj.user.profile.image.url)
        return None

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        if value * 10 % 5 != 0:
            raise serializers.ValidationError("Rating must be in steps of 0.5 (e.g., 3.5, 4.0, 4.5).")
        return Decimal(value)
