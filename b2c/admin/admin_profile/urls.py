from django.urls import path
from . import views

urlpatterns = [
    path("admin-profiles/", views.AdminProfileListCreateAPIView.as_view(), name="adminprofile-list-create"),
    path("admin-profiles/<int:pk>/", views.AdminProfileRetrieveUpdateDestroyAPIView.as_view(), name="adminprofile-detail"),

    path("company/profile", views.CompanyDetailsListCreateAPIView.as_view(), name="company-list-create"),
    path("company-profile/<int:pk>/", views.CompanyDetailsRetrieveUpdateDestroyAPIView.as_view(), name="company-detail"),

    # path("notifications/", views.AdminNotificationListAPIView.as_view(), name="admin-notification-list"),
    # email security
    path("email-preferences/",views. EmailSecurityDetailUpdateView.as_view(), name="email-preferences"),
    path("change-password/",views. ChangePasswordView.as_view(), name="change-password"), 
]
