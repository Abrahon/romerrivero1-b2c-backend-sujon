
from rest_framework import serializers
from .models import UserProfile, Gender
from datetime import date
import re

PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.name", read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'email', 'full_name', 'profile_image', 'profile_image_url',
            'gender', 'date_of_birth', 'country', 'phone_number',
            'contact_email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        read_only_fields = ['email']

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return ""

    def validate_date_of_birth(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("date_of_birth cannot be in the future.")
        return value

    def validate_phone_number(self, value):
        if value and not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value

    def validate_emergency_contact_phone(self, value):
        if value and not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Invalid emergency contact phone format.")
        return value

    def validate_gender(self, value):
        if value not in Gender.values:
            raise serializers.ValidationError("Invalid gender.")
        return value
