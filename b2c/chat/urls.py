from django.urls import path
from .views import SendMessageView, MessageListView, MarkAsReadView

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('list/', MessageListView.as_view(), name='message-list'),
    path('read/<int:pk>/', MarkAsReadView.as_view(), name='mark-read'),
]
