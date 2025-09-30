from rest_framework import serializers
from .models import Message, ChatBot
from accounts.models import User
from django.db.models import Q, Max

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



class UserListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'last_message']

    def get_last_message(self, obj):
        request = self.context.get('request')
        if request and request.user.is_staff:
            last_msg = Message.objects.filter(
                Q(sender=obj, receiver=request.user) | Q(sender=request.user, receiver=obj)
            ).order_by('-timestamp').first()
            if last_msg:
                return {
                    'content': last_msg.content,
                    'timestamp': last_msg.timestamp,
                    'sender': last_msg.sender.email
                }
        return None

class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = ["id", "query", "answer"]



