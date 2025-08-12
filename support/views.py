# support/views.py
from rest_framework import generics
from .models import SupportRequest
from .serializers import SupportRequestSerializer
from rest_framework.permissions import AllowAny

class SupportRequestCreateView(generics.CreateAPIView):
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer
    permission_classes = [AllowAny]

