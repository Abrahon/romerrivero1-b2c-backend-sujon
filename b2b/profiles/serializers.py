from rest_framework import serializers
from .models import CompanyDetails, Notification
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import EmailSecurity, AdminProfile
from django.contrib.auth import get_user_model

import uuid

class AdminProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AdminProfile
        fields = ["first_name", "last_name", "job_title", "bio", "image", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    

class CompanyDetailsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDetails
        fields = ['id', 'company_name', 'industry_type', 'company_email', 'company_phone', 'company_address', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None





class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "notification_type", "is_read", "created_at"]



class EmailSecuritySerializer(serializers.ModelSerializer):
    primary_email = serializers.EmailField(source="user.email", read_only=True)  # read-only

    class Meta:
        model = EmailSecurity
        fields = ["primary_email", "backup_email"]

# class ChangePasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(write_only=True, required=True)
#     new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     confirm_new_password = serializers.CharField(write_only=True, required=True)

#     def validate(self, attrs):
#         if attrs["new_password"] != attrs["confirm_new_password"]:
#             raise serializers.ValidationError({"password": "New passwords do not match"})
#         return attrs

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match"})
        return attrs
