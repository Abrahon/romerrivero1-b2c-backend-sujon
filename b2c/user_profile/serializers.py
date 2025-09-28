# # # accounts/serializers.py
# # import re
# # from rest_framework import serializers
# # from .models import UserProfile, Gender
# # from datetime import date

# # PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

# # class UserProfileSerializer(serializers.ModelSerializer):
# #     user = serializers.PrimaryKeyRelatedField(read_only=True)
# #     full_name = serializers.CharField(source="user.name", read_only=True)
# #     date_of_birth = serializers.DateField(required=False, allow_null=True)
# #     profile_image_url = serializers.SerializerMethodField()

# #     class Meta:
# #         model = UserProfile
# #         fields = [
# #             'user',
# #             'profile_image_url',
# #             'full_name',
# #             'gender',
# #             'date_of_birth',
# #             'country',
# #             'phone_number',
# #             'contact_email',
# #             'address',
# #             'emergency_contact_name',
# #             'emergency_contact_phone',
# #             'emergency_contact_relationship',
# #         ]
# #         read_only_fields = ['user', 'full_name', 'created_at', 'updated_at']

# #     def get_profile_image_url(self, obj):
# #         if obj.profile_image:
# #             return obj.profile_image.url
# #         return None

# #     def update(self, instance, validated_data):
# #         profile_image = validated_data.pop('profile_image', None)
# #         if profile_image:
# #             instance.profile_image = profile_image
# #         return super().update(instance, validated_data)


# #     # Validation methods
# #     def validate_gender(self, value):
# #         if value not in Gender.values:
# #             raise serializers.ValidationError("Invalid gender.")
# #         return value

# #     def validate_phone_number(self, value):
# #         if value and not PHONE_REGEX.match(value):
# #             raise serializers.ValidationError("Invalid phone number format. Use numeric with optional leading +.")
# #         return value

# #     def validate_emergency_contact_phone(self, value):
# #         if value and not PHONE_REGEX.match(value):
# #             raise serializers.ValidationError("Invalid emergency contact phone format.")
# #         return value

# #     def validate_date_of_birth(self, value):
# #         if value and value > date.today():
# #             raise serializers.ValidationError("date_of_birth cannot be in the future.")
# #         return value


# from rest_framework import serializers
# from .models import UserProfile, Gender
# from datetime import date
# import re

# PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(read_only=True)
#     full_name = serializers.CharField(source="user.name", read_only=True)
#     date_of_birth = serializers.DateField(required=False, allow_null=True)
    
#     # Upload image
#     profile_image = serializers.ImageField(required=False, allow_null=True, write_only=True)
#     # Return URL
#     profile_image_url = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = [
#             'user',
#             'profile_image',
#             'profile_image_url',
#             'full_name',
#             'gender',
#             'date_of_birth',
#             'country',
#             'phone_number',
#             'contact_email',
#             'address',
#             'emergency_contact_name',
#             'emergency_contact_phone',
#             'emergency_contact_relationship',
#         ]
#         read_only_fields = ['user', 'full_name', 'created_at', 'updated_at']

#     def get_profile_image_url(self, obj):
#         request = self.context.get('request')
#         if obj.profile_image:
#             if request:
#                 return request.build_absolute_uri(obj.profile_image.url)
#             return obj.profile_image.url
#         return ""

#     def update(self, instance, validated_data):
#         # Handle profile_image separately
#         profile_image = validated_data.pop('profile_image', None)
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         if profile_image:
#             instance.profile_image = profile_image
#         instance.save()
#         return instance

#     # Gender & phone validations
#     def validate_gender(self, value):
#         if value not in Gender.values:
#             raise serializers.ValidationError("Invalid gender.")
#         return value

#     def validate_phone_number(self, value):
#         if value and not PHONE_REGEX.match(value):
#             raise serializers.ValidationError("Invalid phone number format. Use numeric with optional leading +.")
#         return value

#     def validate_emergency_contact_phone(self, value):
#         if value and not PHONE_REGEX.match(value):
#             raise serializers.ValidationError("Invalid emergency contact phone format.")
#         return value

#     def validate_date_of_birth(self, value):
#         if value and value > date.today():
#             raise serializers.ValidationError("date_of_birth cannot be in the future.")
#         return value

from rest_framework import serializers
from .models import UserProfile, Gender
from datetime import date
import re

PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.name", read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    # image = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'full_name', 'profile_image', 'profile_image_url',
            'gender', 'date_of_birth', 'country', 'phone_number',
            'contact_email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        read_only_fields = ['user', 'full_name']

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
