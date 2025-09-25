from rest_framework import serializers
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
from b2c.orders.models import Order

User = get_user_model()


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)   
    profile_image = serializers.ImageField(source="user_profile.profile_image", read_only=True)
    phone_number = serializers.CharField(source="user_profile.phone_number", read_only=True)
    address = serializers.CharField(source="user_profile.address", read_only=True)
    email = serializers.EmailField(read_only=True)

    total_spent = serializers.SerializerMethodField()
    cards_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",             
            "email",
            "phone_number",
            "address",
            "profile_image",
            "total_spent",
            "cards_number",
        ]

    def get_total_spent(self, obj):
        return (
            Order.objects.filter(user=obj)
            .aggregate(total=Sum("total_amount"))["total"] or 0
        )

    def get_cards_number(self, obj):
        return (
            Order.objects.filter(user=obj)
            .aggregate(count=Count("id"))["count"] or 0
        )
