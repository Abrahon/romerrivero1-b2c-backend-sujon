from django.urls import path
from . import views

urlpatterns = [
    path("admin-profiles/", views.AdminProfileListCreateAPIView.as_view(), name="adminprofile-list-create"),
    path("admin-profiles/<int:pk>/", views.AdminProfileRetrieveUpdateDestroyAPIView.as_view(), name="adminprofile-detail"),

    path("companies/", views.CompanyDetailsListCreateAPIView.as_view(), name="company-list-create"),
    path("companies/<int:pk>/", views.CompanyDetailsRetrieveUpdateDestroyAPIView.as_view(), name="company-detail"),

    path("notifications/", views.AdminNotificationListAPIView.as_view(), name="admin-notification-list"),
    # email security
    path("profile/email-preferences/",views. EmailSecurityDetailUpdateView.as_view(), name="email-preferences"),
    path("profile/change-password/",views. ChangePasswordView.as_view(), name="change-password"),
   
]
