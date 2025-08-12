
# accounts/serializers.py
import re
from rest_framework import serializers
from .models import UserProfile, Gender
from datetime import date

PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')  # simple E.164-ish validation

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'profile_image',
            'full_name',
            'gender',
            'date_of_birth',
            'country',
            'phone_number',
            'contact_email',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_gender(self, value):
        if value not in Gender.values:
            raise serializers.ValidationError("Invalid gender.")
        return value

    def validate_phone_number(self, value):
        if value:
            if not PHONE_REGEX.match(value):
                raise serializers.ValidationError("Invalid phone number format. Use numeric with optional leading +.")
        return value

    def validate_emergency_contact_phone(self, value):
        if value:
            if not PHONE_REGEX.match(value):
                raise serializers.ValidationError("Invalid emergency contact phone format.")
        return value

    def validate_date_of_birth(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("date_of_birth cannot be in the future.")
        return value
