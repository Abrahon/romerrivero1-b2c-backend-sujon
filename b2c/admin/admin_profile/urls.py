from django.urls import path
from . import views

urlpatterns = [
    path("admin-profile/", views.AdminProfileView.as_view(), name="adminprofile-detail"),

    path("company-profile/", views.CompanyDetailsRetrieveUpdateDestroyAPIView.as_view(), name="company-list-create"),

    path("notifications/", views.AdminNotificationListAPIView.as_view(), name="admin-notification-list"),
    # email security
    path("email-security/",views. EmailSecurityDetailUpdateView.as_view(), name="email-preferences"),
    path("change-password/",views. ChangePasswordView.as_view(), name="change-password"),
   
]
