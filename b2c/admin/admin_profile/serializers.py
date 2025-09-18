from rest_framework import serializers
from .models import CompanyDetails
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import EmailSecurity, AdminProfile
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

import uuid

class AdminProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AdminProfile
        fields = ["id", "first_name", "last_name", "job_title", "bio", "image", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            
            return obj.image.url
        return None


    

class CompanyDetailsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDetails
        fields = ['id', 'company_name', 'industry_type', 'company_email', 'company_phone', 'company_address', 'image', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            
            return obj.image.url
        return None





class EmailSecuritySerializer(serializers.ModelSerializer):
    primary_email = serializers.EmailField(source="user.email", read_only=True) 

    class Meta:
        model = EmailSecurity
        fields = ["primary_email", "backup_email"]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'},
        error_messages={'required': _('Current password is required')}
    )
    new_password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        error_messages={'required': _('New password is required')}
    )
    confirm_new_password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'},
        error_messages={'required': _('Please confirm your new password')}
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Current password is incorrect'))
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': _('New passwords do not match')})
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': _('New password cannot be the same as the current password')})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

