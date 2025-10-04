# b2c/chat/urls.py
from django.urls import path
from .views import (
    UserConversationListView,
    UserConversationView,
    AdminConversationView,
    SendMessageView,
    MyConversationListView,
    AdminSendMessageView,
    UpdateDeleteMessageView,
    TrainingDataListCreateView,
    TrainingDataDetailView,
    ChatQueryView,
    ChatBotQueryStatsView,
    ChatBotQueryListView,
)
 


urlpatterns = [
    # -------------------- User Endpoints --------------------
    path('user/messages/', UserConversationView.as_view(), name='user_conversations'),
    path('user/message/send/', SendMessageView.as_view(), name='send_message_to_admin'),
    path('user/my-conversations/', MyConversationListView.as_view(), name='my_conversations'),

    # -------------------- Admin Endpoints --------------------
    path('admin/users-conversations-list/', UserConversationListView.as_view(), name='users_with_conversations'),
    path('admin/conversation/<int:user_id>/', AdminConversationView.as_view(), name='admin_conversation_with_user'),
    path('admin/message/send/', AdminSendMessageView.as_view(), name='admin_send_message'),

    # -------------------- Update / Delete Messages --------------------
    path('message/<int:pk>/', UpdateDeleteMessageView.as_view(), name='update_delete_message'),

    # -------------------- ChatBot --------------------
    path('train_data/', TrainingDataListCreateView.as_view(), name='train-data-list-create'),
    path('train_data/<int:id>/', TrainingDataDetailView.as_view(), name='train-data-detail'),
    path('query/', ChatQueryView.as_view(), name='chat-query'),
    path('history/', ChatBotQueryListView.as_view(), name='chat-history'),
    path('admin/history/', ChatBotQueryStatsView.as_view(), name='chat-history'),

 ]
