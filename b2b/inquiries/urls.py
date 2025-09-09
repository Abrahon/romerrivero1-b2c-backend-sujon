from django.urls import path
from .views import (
    InquiryListCreateView,
    InquiryUpdateDeleteView,
    AdminNotificationListView,
    MarkNotificationReadView
)

urlpatterns = [
    # Inquiries
    path('inquiries/', InquiryListCreateView.as_view(), name='inquiry-list-create'),
    path('inquiries/<int:pk>/', InquiryUpdateDeleteView.as_view(), name='inquiry-update-delete'),

    # Admin Notifications
    path('admin/notifications/', AdminNotificationListView.as_view(), name='admin-notifications'),
    path('admin/notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
