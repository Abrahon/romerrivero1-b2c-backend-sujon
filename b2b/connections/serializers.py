from rest_framework import serializers
from .models import Connection
from .models import CompanyCategory, ConnectionCategory

class ConnectionSerializer(serializers.ModelSerializer):
    company_category = serializers.ChoiceField(choices=CompanyCategory.choices)
    connection_category = serializers.ChoiceField(choices=ConnectionCategory.choices)

    class Meta:
        model = Connection
        fields = ['id', 'name', 'company_category', 'connection_category', 'email', 'phone', 'address', 'notes', 'is_active']
        read_only_fields = ['id']


