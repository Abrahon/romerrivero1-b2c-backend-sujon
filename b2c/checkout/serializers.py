from rest_framework import serializers
from .models import Shipping

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        models = Shipping
        fields = '__all__'
        read_only_fields = ['user']
        

