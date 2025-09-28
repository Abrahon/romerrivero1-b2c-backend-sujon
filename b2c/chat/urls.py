
# from django.urls import path
# from .views import (
#     SendMessageView,
#     MessageListView,
#     MarkMessageReadView,
#     UpdateMessageView,
#     # ReplyMessageView,
#     DeleteMessageView,
#     # AdminMessageListView,  # Added
#     ChatBotList,
#     ChatBotCreateView,
#     # AdminMessageListView,
# )

# urlpatterns = [
#     # ---------------------------
#     # User routes
#     # ---------------------------
#     path('messages/send/', SendMessageView.as_view(), name='send-message'),
#     # List messages (User: own + admin messages)
#     path('messages/list/', MessageListView.as_view(), name='list-messages'),
#     # Update a message (sender or receiver)
#     path('messages/<int:pk>/update/', UpdateMessageView.as_view(), name='update-message'),
#     # Delete a message (admin or sender/receiver)
#     path('messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete-message'),

#     # ---------------------------
#     # Admin routes
#     # ---------------------------
#     # Admin: List all messages from all users
#     # path('admin/messages/', AdminMessageListView.as_view(), name='admin-message-list'),

#     # Admin marks a message as read
#     path('admin/messages/<int:pk>/mark-read/', MarkMessageReadView.as_view(), name='admin-mark-read'),
#     # Admin replies to a message
#     #  path('admin/messages/reply/<int:user_id>/', ReplyMessageView.as_view(), name='admin-reply-user'),
#     path('get-chatbot/', ChatBotList.as_view()),
#     path('chatbot/', ChatBotCreateView.as_view())
# ]

from django.urls import path
from .views import (
    SendMessageView, MessageListView, AdminUserMessagesView, AdminSendMessageView,
    MarkMessageReadView, DeleteMessageView, UpdateMessageView,
    ChatBotList, ChatBotCreateView,UserListView
)

urlpatterns = [
    # User messages
    path('messages/send/', SendMessageView.as_view(), name='send_message'),
    path('messages/', MessageListView.as_view(), name='list_messages'),
    path('messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete_message'),
    path('messages/<int:pk>/update/', UpdateMessageView.as_view(), name='update_message'),

    # Admin
     path('admin/users/list/', UserListView.as_view(), name='user_list'),
    path('admin/messages/<int:user_id>/', AdminUserMessagesView.as_view(), name='admin_user_messages'),
    path('admin/messages/send/', AdminSendMessageView.as_view(), name='admin_send_message'),
    path('admin/messages/<int:pk>/read/', MarkMessageReadView.as_view(), name='mark_read'),

    # ChatBot
    path('chatbot/', ChatBotList.as_view(), name='chatbot_list'),
    path('chatbot/create/', ChatBotCreateView.as_view(), name='chatbot_create'),
]
