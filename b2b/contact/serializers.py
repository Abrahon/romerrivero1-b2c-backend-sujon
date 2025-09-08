from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "created_at"]

    def validate_message(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Message must be at least 5 characters long.")
        return value
