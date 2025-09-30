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

# User = get_user_model()

# # # -------------------- User sends message --------------------
# # class SendMessageView(generics.CreateAPIView):
# #     serializer_class = MessageSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def perform_create(self, serializer):
# #         receiver_id = self.request.data.get("receiver")
# #         serializer.save(sender=self.request.user, receiver_id=receiver_id)


# # -------------------- List messages for user --------------------
# class MessageListView(generics.ListAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         # For admin, show all messages
#         if user.is_staff:
#             return Message.objects.all()
#         # Normal user: messages where user is sender or receiver
#         return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)
    
# # user list 
# class UserListView(generics.ListAPIView):
#     serializer_class = UserListSerializer
#     permission_classes = [IsAdminUser]
    
#     def get_queryset(self):
#         # Return all users except the admin themselves
#         return User.objects.exclude(id=self.request.user.id)
    


    
# # -------------------- Admin sees messages for a specific user --------------------
# class AdminUserMessagesView(generics.ListAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [IsAdminUser]

#     def get_queryset(self):
#         user_id = self.kwargs['user_id']
#         user = get_object_or_404(User, id=user_id)
#         # All messages between admin and this user
#         return Message.objects.filter(sender__in=[user, self.request.user],
#                                       receiver__in=[user, self.request.user]).order_by('timestamp')


# # -------------------- Admin sends message to a user --------------------
# class AdminSendMessageView(generics.CreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [IsAdminUser]

#     def perform_create(self, serializer):
#         user_id = self.request.data.get("receiver")
#         if not user_id:
#             raise serializers.ValidationError({"receiver": "User ID is required"})
#         serializer.save(sender=self.request.user, receiver_id=user_id)


# # -------------------- Mark message read --------------------
# class MarkMessageReadView(APIView):
#     permission_classes = [IsAdminUser]

#     def patch(self, request, pk):
#         message = get_object_or_404(Message, id=pk)
#         message.is_read = True
#         message.save(update_fields=['is_read'])
#         return Response({"status": "marked as read"}, status=status.HTTP_200_OK)


# # -------------------- Delete message --------------------
# class DeleteMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, pk):
#         message = get_object_or_404(Message, id=pk)
#         if not (request.user.is_staff or message.sender == request.user):
#             return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
#         message.delete()
#         return Response({"status": "Message deleted"}, status=status.HTTP_200_OK)


# # -------------------- Update message --------------------
# class UpdateMessageView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, pk):
#         message = get_object_or_404(Message, id=pk)
#         if not (request.user == message.sender or request.user == message.receiver):
#             return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

#         content = request.data.get('content')
#         if not content:
#             return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

#         message.content = content
#         message.save(update_fields=['content'])
#         serializer = MessageSerializer(message)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# b2c/chat/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from accounts.models import User
from .models import Message, ChatBot
from .serializers import MessageSerializer, UserListSerializer, ChatBotSerializer
from accounts.permissions import IsAdminUser
from django.db.models import Max, Q, F
from django.db.models.functions import Coalesce


# -------------------- Admin: list of users with conversations --------------------


class UserConversationListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class=None

    def get_queryset(self):
        admin = self.request.user

        # Get all user IDs that have messaged admin
        user_ids = Message.objects.filter(Q(sender=admin) | Q(receiver=admin)) \
            .values_list("sender", "receiver")
        ids = {uid for pair in user_ids for uid in pair if uid != admin.id}
        qs = User.objects.filter(id__in=ids)

        # Annotate last message timestamp correctly
        qs = qs.annotate(
            last_sent=Max("sent_messages__timestamp", filter=Q(sent_messages__receiver=admin)),
            last_received=Max("received_messages__timestamp", filter=Q(received_messages__sender=admin)),
        ).annotate(
            last_msg_time=Coalesce(F("last_sent"), F("last_received"))
        ).order_by("-last_msg_time")

        return qs



from rest_framework import generics, permissions
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Message, User
from .serializers import MessageSerializer


class UserConversationView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        # All messages between this user and any admin
        return Message.objects.filter(
            Q(sender=user, receiver__is_staff=True) | Q(sender__is_staff=True, receiver=user)
        ).order_by("timestamp")

    def perform_create(self, serializer):
        """
        Save message where the sender is the logged-in user
        and receiver is an admin (you can adjust logic as needed).
        """
        serializer.save(sender=self.request.user)

# user convirsession


from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Q
from accounts.models import User
from b2c.chat.models import Message
from b2c.chat.serializers import MessageSerializer


class AdminConversationView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

    def get_queryset(self):
        admin = self.request.user  # logged-in admin
        other_user_id = self.kwargs.get("user_id")

        # Ensure the target is a normal user (not staff)
        other_user = get_object_or_404(User, id=other_user_id, is_staff=False)

        # ✅ Only messages between THIS admin and THIS specific user
        return Message.objects.filter(
    Q(sender=other_user) | Q(receiver=other_user)
).select_related("sender", "receiver").order_by("timestamp")







# -------------------- User sends message to admin --------------------
class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class=None

    def perform_create(self, serializer):
        user = self.request.user
        admin_user = User.objects.filter(is_staff=True).first()  # Assuming single admin
        if not admin_user:
            raise serializers.ValidationError({"receiver": "Admin not found."})
        serializer.save(sender=user, receiver=admin_user)



class MyConversationListView(generics.ListAPIView):
    """
    Returns a list of users the logged-in user has had conversations with,
    along with the last message timestamp for ordering.
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        # Get all user IDs that this user has messaged or received messages from
        user_ids = Message.objects.filter(Q(sender=user) | Q(receiver=user)) \
            .values_list("sender", "receiver")
        ids = {uid for pair in user_ids for uid in pair if uid != user.id}

        # Get users and annotate last message timestamp
        qs = User.objects.filter(id__in=ids).annotate(
            last_sent=Max("sent_messages__timestamp", filter=Q(sent_messages__receiver=user)),
            last_received=Max("received_messages__timestamp", filter=Q(received_messages__sender=user)),
        ).annotate(
            last_msg_time=Coalesce(F("last_sent"), F("last_received"))
        ).order_by("-last_msg_time")

        return qs

# -------------------- Admin sends message to user --------------------
class AdminSendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]
    pagination_class=None

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")
        if not receiver_id:
            raise serializers.ValidationError({"receiver": "User ID is required."})
        receiver = get_object_or_404(User, id=receiver_id)
        serializer.save(sender=self.request.user, receiver=receiver)


# -------------------- Update / Delete message --------------------
class UpdateDeleteMessageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class=None
    queryset = Message.objects.all()

    def perform_update(self, serializer):
        message = self.get_object()
        if message.sender != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own messages.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.sender != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You cannot delete this message.")
        instance.delete()


# -------------------- ChatBot --------------------
class ChatBotList(generics.ListAPIView):
    serializer_class = ChatBotSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class=None
    queryset = ChatBot.objects.all()


class ChatBotCreateView(generics.CreateAPIView):
    serializer_class = ChatBotSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class=None
    

    def perform_create(self, serializer):
        query = self.request.data.get("query")
        if not query:
            raise serializers.ValidationError({"query": "Query is required."})
        serializer.save(user=self.request.user, query=query)
