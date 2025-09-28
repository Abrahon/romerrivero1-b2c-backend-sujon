# notifications/urls.py
from django.urls import path
from .views import NotificationListView, MarkNotificationReadView

urlpatterns = [
    path('list/', NotificationListView.as_view(), name='notifications-list'),
    path('read/<int:pk>/', MarkNotificationReadView.as_view(), name='notification-read'),
]
   