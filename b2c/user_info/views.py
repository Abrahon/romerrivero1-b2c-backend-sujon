from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import UserProfile, CompanyDetails
from .serializers import UserProfileSerializer, CompanyDetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer

# from django.core.mail import send_mail
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Notification



class UserProfileListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]  #  This line makes it public


class UserProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = [AllowAny]


class CompanyDetailsListCreateAPIView(generics.ListCreateAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = [AllowAny]


class CompanyDetailsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyDetails.objects.all()
    serializer_class = CompanyDetailsSerializer
    parser_classes = [AllowAny]

# notification

# class ContactView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         subject = request.data.get('subject')
#         message = request.data.get('message')

#         send_mail(
#             subject,
#             message,
#             request.user.email,
#             ['admin@example.com'],  # Change to your admin/receiver
#             fail_silently=False,
#         )

#         Notification.objects.create(
#             user=request.user,
#             message=f"Message sent: {subject}"
#         )

#         return Response({'status': 'Message sent and notification created'})

# user_info/views.py


# get notificastion from user 
class UserNotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [AllowAny]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
