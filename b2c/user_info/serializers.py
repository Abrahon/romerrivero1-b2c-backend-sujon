from rest_framework import serializers
from .models import UserProfile, CompanyDetails
from rest_framework import serializers
from .models import Notification

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = '__all__'

# user_info/serializers.py



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'notification_type', 'is_read', 'created_at']
