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
    # path('chatbot/', ChatBotList.as_view(), name='chatbot_list'),
    # path('chatbot/create/', ChatBotCreateView.as_view(), name='chatbot_create'),
]

