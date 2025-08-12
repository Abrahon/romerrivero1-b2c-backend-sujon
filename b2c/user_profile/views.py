from django.shortcuts import render

# Create your views here.
# accounts/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profile/       -> retrieve current user's profile (auto-create if none)
    PUT  /api/profile/       -> replace profile fields
    PATCH /api/profile/      -> partial update (recommended for image uploads)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        # create profile if not exists (convenience)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AdminUserProfileListView(generics.ListAPIView):
    """
    For admin: list all profiles
    """
    queryset = UserProfile.objects.all().order_by('-updated_at')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
