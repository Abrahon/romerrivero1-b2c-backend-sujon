from rest_framework import serializers
from .models import Message, ChatBot
from accounts.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source='sender.email')
    receiver_email = serializers.ReadOnlyField(source='receiver.email')

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_email', 'receiver', 'receiver_email',
            'content', 'is_read', 'timestamp', 'parent'
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'timestamp', 'sender_email', 'receiver_email']

    def get_replies(self, obj):
        return MessageSerializer(obj.replies.all(), many=True).data

class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = ["id", "query", "answer"]

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserListSerializer(serializers.ModelSerializer):
    unread_messages_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'is_active',
            'date_joined',
            'unread_messages_count',
            'last_message'
        ]
    
    def get_unread_messages_count(self, obj):
        # Count unread messages from admin to this user
        request = self.context.get('request')
        if request and request.user.is_staff:
            return Message.objects.filter(receiver=obj, sender=request.user, is_read=False).count()
        return 0
    
    def get_last_message(self, obj):
        # Get the last message between admin and this user
        request = self.context.get('request')
        if request and request.user.is_staff:
            last_message = Message.objects.filter(
                sender__in=[obj, request.user],
                receiver__in=[obj, request.user]
            ).order_by('-timestamp').first()
            
            if last_message:
                return {
                    'content': last_message.content,
                    'timestamp': last_message.timestamp,
                    'is_read': last_message.is_read,
                    'sender': last_message.sender.email
                }
        return None