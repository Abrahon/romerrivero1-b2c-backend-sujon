from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.permissions import IsAdminUser
from .models import Message
from .serializers import MessageSerializer


# Buyer sends message
class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")
        serializer.save(sender=self.request.user, receiver_id=receiver_id)


# List messages
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Message.objects.all()
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)


# Admin marks message as read
class MarkMessageReadView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        message = get_object_or_404(Message, id=pk)
        message.is_read = True
        message.save(update_fields=['is_read'])
        return Response({"status": "marked as read"}, status=status.HTTP_200_OK)


from django.contrib.auth import get_user_model

User = get_user_model()

class ReplyMessageView(APIView):
    """
    Admin replies to the latest message from a user.
    POST /api/admin/messages/reply/<user_id>/
    """
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        # Get the user
        user = get_object_or_404(User, id=user_id)

        # Get the latest message from this user (ignore receiver field)
        parent_message = (
            Message.objects.filter(sender=user)
            .order_by('-timestamp')  # timestamp field from your model
            .first()
        )

        if not parent_message:
            return Response(
                {"error": "This user has not sent any messages yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get content from request
        content = request.data.get("content")
        if not content or content.strip() == "":
            return Response(
                {"error": "Message content is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create reply message
        reply = Message.objects.create(
            sender=request.user,   # Admin
            receiver=user,         # Original user
            content=content.strip(),
            parent=parent_message
        )

        serializer = MessageSerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Delete message
class DeleteMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        message = get_object_or_404(Message, id=pk)
        if not (request.user.is_staff or message.sender == request.user):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        message.delete()
        return Response({"status": "Message deleted"}, status=status.HTTP_200_OK)


class UpdateMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        message = get_object_or_404(Message, id=pk)

        # Only sender or receiver can update
        if not (request.user == message.sender or request.user == message.receiver):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        content = request.data.get('content')
        if not content:
            return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        message.content = content
        message.save(update_fields=['content'])
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Message.objects.all()
    
from .serializers import ChatBotSerializer
from .models import ChatBot
class ChatBotList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatBotSerializer
    queryset = ChatBot.objects.all()


class ChatBotCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Get 'query' from request body
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create ChatBot entry
        chatbot = ChatBot.objects.create(user=request.user, query=query)

        # Serialize and return
        serializer = ChatBotSerializer(chatbot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)