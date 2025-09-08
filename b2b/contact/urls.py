from django.urls import path
from .views import ContactMessageCreateAPIView,AdminNotificationListView,MarkNotificationReadView

urlpatterns = [
    path("contact-now/", ContactMessageCreateAPIView.as_view(), name="contact-now"),
    path("admin/notifications/", AdminNotificationListView.as_view(), name="admin-notifications"),
    path("admin/notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),
]
      