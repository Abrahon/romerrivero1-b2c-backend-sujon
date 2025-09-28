from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.permissions import IsAdminUser
from .models import Message
from .serializers import MessageSerializer


# # Buyer sends message
class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")
        serializer.save(sender=self.request.user, receiver_id=receiver_id)


# # List messages
# class MessageListView(generics.ListAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return Message.objects.all()
#         return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)


# # Admin marks message as read
# class MarkMessageReadView(APIView):
#     permission_classes = [IsAdminUser]

#     def patch(self, request, pk):
#         message = get_object_or_404(Message, id=pk)
#         message.is_read = True
#         message.save(update_fields=['is_read'])
#         return Response({"status": "marked as read"}, status=status.HTTP_200_OK)


# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ReplyMessageView(APIView):
#     """
#     Admin replies to the latest message from a user.
#     POST /api/admin/messages/reply/<user_id>/
#     """
#     permission_classes = [IsAdminUser]

#     def post(self, request, user_id):
#         # Get the user
#         user = get_object_or_404(User, id=user_id)

#         # Get the latest message from this user (ignore receiver field)
#         parent_message = (
#             Message.objects.filter(sender=user)
#             .order_by('-timestamp')  # timestamp field from your model
#             .first()
#         )

#         if not parent_message:
#             return Response(
#                 {"error": "This user has not sent any messages yet."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Get content from request
#         content = request.data.get("content")
#         if not content or content.strip() == "":
#             return Response(
#                 {"error": "Message content is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # # Create reply message
#         # reply = Message.objects.create(
#         #     sender=request.user,   # Admin
#         #     receiver=user,         # Original user
#         #     content=content.strip(),
#         #     parent=parent_message
#         # )

#         # serializer = MessageSerializer(reply)
#         # return Response(serializer.data, status=status.HTTP_201_CREATED)


# # Delete message
# class DeleteMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, pk):
#         message = get_object_or_404(Message, id=pk)
#         if not (request.user.is_staff or message.sender == request.user):
#             return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

#         message.delete()
#         return Response({"status": "Message deleted"}, status=status.HTTP_200_OK)


# class UpdateMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, pk):
#         message = get_object_or_404(Message, id=pk)

#         # Only sender or receiver can update
#         if not (request.user == message.sender or request.user == message.receiver):
#             return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

#         content = request.data.get('content')
#         if not content:
#             return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

#         message.content = content
#         message.save(update_fields=['content'])
#         serializer = MessageSerializer(message)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
# class AdminMessageListView(generics.ListAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [IsAdminUser]

#     def get_queryset(self):
#         return Message.objects.all()
    
# from .serializers import ChatBotSerializer
# from .models import ChatBot
# class ChatBotList(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ChatBotSerializer
#     queryset = ChatBot.objects.all()


# class ChatBotCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         # Get 'query' from request body
#         query = request.data.get("query")
#         if not query:
#             return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)



#         # Create ChatBot entry
#         chatbot = ChatBot.objects.create(user=request.user, query=query)


#         # Serialize and return
#         serializer = ChatBotSerializer(chatbot)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Message, ChatBot
from .serializers import MessageSerializer, ChatBotSerializer
from accounts.permissions import IsAdminUser
from .serializers import MessageSerializer,UserListSerializer

User = get_user_model()

# # -------------------- User sends message --------------------
# class SendMessageView(generics.CreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         receiver_id = self.request.data.get("receiver")
#         serializer.save(sender=self.request.user, receiver_id=receiver_id)


# -------------------- List messages for user --------------------
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # For admin, show all messages
        if user.is_staff:
            return Message.objects.all()
        # Normal user: messages where user is sender or receiver
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)
    
# user list 
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        # Return all users except the admin themselves
        return User.objects.exclude(id=self.request.user.id)
    


    
# -------------------- Admin sees messages for a specific user --------------------
class AdminUserMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        # All messages between admin and this user
        return Message.objects.filter(sender__in=[user, self.request.user],
                                      receiver__in=[user, self.request.user]).order_by('timestamp')


# -------------------- Admin sends message to a user --------------------
class AdminSendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        user_id = self.request.data.get("receiver")
        if not user_id:
            raise serializers.ValidationError({"receiver": "User ID is required"})
        serializer.save(sender=self.request.user, receiver_id=user_id)


# -------------------- Mark message read --------------------
class MarkMessageReadView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        message = get_object_or_404(Message, id=pk)
        message.is_read = True
        message.save(update_fields=['is_read'])
        return Response({"status": "marked as read"}, status=status.HTTP_200_OK)


# -------------------- Delete message --------------------
class DeleteMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        message = get_object_or_404(Message, id=pk)
        if not (request.user.is_staff or message.sender == request.user):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({"status": "Message deleted"}, status=status.HTTP_200_OK)


# -------------------- Update message --------------------
class UpdateMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        message = get_object_or_404(Message, id=pk)
        if not (request.user == message.sender or request.user == message.receiver):
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        content = request.data.get('content')
        if not content:
            return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        message.content = content
        message.save(update_fields=['content'])
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------- ChatBot --------------------
class ChatBotList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatBotSerializer
    queryset = ChatBot.objects.all()


class ChatBotCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
        chatbot = ChatBot.objects.create(user=request.user, query=query)
        serializer = ChatBotSerializer(chatbot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
