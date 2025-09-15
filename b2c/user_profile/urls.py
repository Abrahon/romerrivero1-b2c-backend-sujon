from django.urls import path
from .views import UserProfileView, AdminUserProfileListView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('admin/profiles/', AdminUserProfileListView.as_view(), name='admin-user-profiles'),
]
