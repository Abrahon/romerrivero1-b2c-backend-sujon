from rest_framework import serializers
from .models import SupportRequest

class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ['id', 'name', 'email', 'message', 'submitted_at']
        read_only_fields = ['id','submitted_at']
