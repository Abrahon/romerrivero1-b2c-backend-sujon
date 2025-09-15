from django.urls import path
from .views import (
    SendMessageView,
    MessageListView,
    MarkMessageReadView,
    UpdateMessageView,
    ReplyMessageView,
    DeleteMessageView,
)

urlpatterns = [
    # Buyer sends a message
    path('messages/send/', SendMessageView.as_view(), name='send-message'),
    # List messages (Admin: all, User: their own)
    path('messages/list/', MessageListView.as_view(), name='list-messages'),
    # Admin marks a message as read
    path('messages/<int:pk>/mark-read/', MarkMessageReadView.as_view(), name='mark-read'),
    # Update a message (both sender and receiver)
    path('messages/<int:pk>/update/', UpdateMessageView.as_view(), name='update-message'),
    # Reply to a message (admin or user)
    path('messages/<int:pk>/reply/', ReplyMessageView.as_view(), name='reply-message'),
    # Delete a message (admin or sender/receiver)
    path('messages/<int:pk>/delete/', DeleteMessageView.as_view(), name='delete-message'),
]
