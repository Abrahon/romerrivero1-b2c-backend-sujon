from django.urls import path
from .views import SendMessageView, MessageListView, MarkMessageReadView

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('list/', MessageListView.as_view(), name='message-list'),
    path('<int:pk>/mark-read/', MarkMessageReadView.as_view(), name='mark-read'),
]
# mark-read/