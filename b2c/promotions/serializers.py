
from rest_framework import serializers
from .models import HeroPromotion, HeroPromotions

class HeroPromotionSerializer(serializers.ModelSerializer):
    hero_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = HeroPromotion
        fields = "__all__"
        read_only_fields = ["id", "user"]

    def validate_first_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("First title must be at least 3 characters long.")
        return value

    def validate_second_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Second title must be at least 3 characters long.")
        return value

    def validate_description(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        if len(value.strip()) > 255:
            raise serializers.ValidationError("Description cannot exceed 255 characters.")
        return value

    def validate_product_link(self, value):
        if value and not value.startswith(("http://", "https://")):
            raise serializers.ValidationError("Product link must start with http:// or https://")
        return value

    def validate(self, attrs):
        if attrs.get("first_title") == attrs.get("second_title"):
            raise serializers.ValidationError("First title and second title cannot be the same.")
        return attrs

class HeroPromotionsSerializer(HeroPromotionSerializer):
    class Meta(HeroPromotionSerializer.Meta):
        model = HeroPromotions
    
    class Meta:
        model = HeroPromotion
        fields = "__all__"
        read_only_fields = ["id", "user"]

    def validate_first_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("First title must be at least 3 characters long.")
        return value

    def validate_second_title(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Second title must be at least 3 characters long.")
        return value

    def validate_description(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        if len(value.strip()) > 255:
            raise serializers.ValidationError("Description cannot exceed 255 characters.")
        return value

    def validate_product_link(self, value):
        if value and not value.startswith(("http://", "https://")):
            raise serializers.ValidationError("Product link must start with http:// or https://")
        return value

    def validate(self, attrs):
        if attrs.get("first_title") == attrs.get("second_title"):
            raise serializers.ValidationError("First title and second title cannot be the same.")
        return attrs
