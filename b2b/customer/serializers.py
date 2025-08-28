# b2b/customers/serializers.py
from rest_framework import serializers
from .models import Customer
from b2b.order.models import Order

class CustomerSerializer(serializers.ModelSerializer):
    total_orders = serializers.ReadOnlyField()
    total_spent = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = ['id', 'user', 'company_name', 'phone', 'email', 'status', 'total_orders', 'total_spent']
