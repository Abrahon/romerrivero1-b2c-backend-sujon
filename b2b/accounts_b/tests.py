from django.test import TestCase

# Create your tests here.
# accounts/urls.py

from django.urls import path, include
from .views import SignupView, LoginView, SendOTPView, VerifyOTPView, ResetPasswordView, AdminCreateView

urlpatterns = [
    # Your custom authentication views
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    # path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('admin/create/', AdminCreateView.as_view(), name='admin-create'),

    # Social login URLs from django-allauth
    path('social/', include('allauth.socialaccount.urls')),  # Social login (Google, Facebook, Twitter)
]
