

from django.urls import path, include
from .views import B2BSignupView, B2BLoginView, B2BSendOTPView, B2BVerifyOTPView, B2BResetPasswordView, B2BAdminCreateView

urlpatterns = [
    path('signup/', B2BSignupView.as_view(), name='signup'),
    path('login/', B2BLoginView.as_view(), name='login'),
    path('send-otp/', B2BSendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', B2BVerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', B2BResetPasswordView.as_view(), name='reset-password'),
    path('admin/create/', B2BAdminCreateView.as_view(), name='admin-create'),

    # Social login URLs from django-allauth
    path('social/', include('allauth.socialaccount.urls')),  # Social login (Google, Facebook, Twitter)
]
