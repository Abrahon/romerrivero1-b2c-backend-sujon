from django.urls import path
from . import views

urlpatterns = [
    path('user-profiles/', views.UserProfileListCreateAPIView.as_view(), name='userprofile-list-create'),
    path('user-profiles/<int:pk>/', views.UserProfileRetrieveUpdateDestroyAPIView.as_view(), name='userprofile-detail'),
    
    path('companies/', views.CompanyDetailsListCreateAPIView.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', views.CompanyDetailsRetrieveUpdateDestroyAPIView.as_view(), name='company-detail'),
    path('notifications/',views. UserNotificationListAPIView.as_view(), name='notification-list'),
    
]
