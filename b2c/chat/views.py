from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Max, Q, F
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from accounts.models import User
from accounts.permissions import IsAdminUser
from .models import Message, TrainData, ChatBotQuery
from .serializers import (
    MessageSerializer,
    UserListSerializer,
    TrainDataSerializer,
    ChatBotQuerySerializer,
    ChatQuerySerializer,
)
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import ChatBotQuerySerializer


AI_BASE_URL = "http://127.0.0.1:8080"  

# # Buyer sends message
class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")
        serializer.save(sender=self.request.user, receiver_id=receiver_id)



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



# Chatbot 
# -------------------------------
# Training Data Views
# -------------------------------
class TrainingDataListCreateView(generics.ListCreateAPIView):
    queryset = TrainData.objects.all().order_by("-id")
    serializer_class = TrainDataSerializer
    pagination_class = None

    def perform_create(self, serializer):
        training_data = serializer.save()
        # Send data to AI model
        payload = {
            "category": training_data.category,
            "context": training_data.context,
            "question": training_data.question,
            "ai_response": training_data.ai_response,
            "keywords": training_data.keywords,
        }
        try:
            requests.post(f"{AI_BASE_URL}/train_data", json=payload, timeout=10)
        except requests.RequestException:
            pass  # Fail silently if AI server is down


class TrainingDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainData.objects.all()
    serializer_class = TrainDataSerializer
    pagination_class = None
    lookup_field = "id"

    def perform_update(self, serializer):
        training_data = serializer.save()
        payload = {
            "category": training_data.category,
            "context": training_data.context,
            "question": training_data.question,
            "ai_response": training_data.ai_response,
            "keywords": training_data.keywords,
        }
        try:
            requests.post(f"{AI_BASE_URL}/train_data", json=payload, timeout=10)
        except requests.RequestException:
            pass


# -------------------------------
# Chat Query
# -------------------------------
class ChatQueryView(APIView):
    pagination_class = None
    """
    Send query to AI model and save response
    """
    def post(self, request):
        serializer = ChatQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_text = serializer.validated_data["query"]
        

        # Send to AI model
        try:
            ai_response = requests.post(
                f"{AI_BASE_URL}/query",
                json={"query": query_text},
                timeout=30
            ).json()
        except requests.Timeout:
            return Response({"error": "AI model timed out"}, status=504)
        except requests.RequestException as e:
            return Response({"error": "AI model unavailable", "details": str(e)}, status=503)

        # Extract the actual AI answer
        answer_text = ai_response.get("answer", {}).get("result", "")
        # ai_response.get("answer", {}).get("result", "") 

        # Save chat history
        chat = ChatBotQuery.objects.create(
            user=request.user,
            query=query_text,
            ai_response=answer_text
        )

        response_data = {
            "query": query_text,
            "ai_response": answer_text,
            "chat_id": chat.id
        }

        return Response(response_data, status=status.HTTP_200_OK)


# -------------------------------
# Chat History
# -------------------------------
class ChatBotQueryListView(generics.ListAPIView):
    serializer_class = ChatBotQuerySerializer
    pagination_class = None

    def get_queryset(self):
        return ChatBotQuery.objects.filter(user=self.request.user).order_by("-created_at")




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class ChatBotQueryStatsView(generics.ListAPIView):
    serializer_class = ChatBotQuerySerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = ChatBotQuery.objects.all().order_by("-created_at")

        # Search by query text or AI response
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(query__icontains=search) | Q(ai_response__icontains=search)
            )

        # Filter by user email
        user_email = self.request.query_params.get("user_email")
        if user_email:
            queryset = queryset.filter(user__email__icontains=user_email)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        # Stats (use the full queryset, not just the paginated page)
        total_conversations = queryset.count()
        qualified_leads = queryset.filter(
            ai_response__iregex=r'qualified|interested|yes'
        ).count()
        conversation_rate = (qualified_leads / total_conversations * 100) if total_conversations > 0 else 0

        # Recent conversations (last 5 overall)
        recent_conversations = queryset[:5]
        recent_serializer = self.get_serializer(recent_conversations, many=True)

        response_data = {
            "total_conversations": total_conversations,
            "qualified_leads": qualified_leads,
            "conversation_rate": round(conversation_rate, 2),
            "recent_conversations": recent_serializer.data,
        }

        # Include paginated results
        return self.get_paginated_response({
            **response_data,
            "all_chat_history": serializer.data
        })
