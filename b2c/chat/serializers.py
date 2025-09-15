from rest_framework import serializers
from .models import Message
from accounts.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source='sender.email')
    receiver_email = serializers.ReadOnlyField(source='receiver.email')
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_email', 'receiver', 'receiver_email',
            'content', 'is_read', 'timestamp', 'parent', 'replies'
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'timestamp', 'sender_email', 'receiver_email', 'replies']

    def get_replies(self, obj):
        return MessageSerializer(obj.replies.all(), many=True).data
