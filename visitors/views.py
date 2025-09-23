# visitors/views.py
from rest_framework import generics, permissions
from .models import Visitor
from .serializers import VisitorSerializer
from datetime import datetime, timedelta

# List all visitors (admin only)
class VisitorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = VisitorSerializer
    queryset = Visitor.objects.all().order_by('-last_visit')


# Visitors today
class TodayVisitorsView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = VisitorSerializer

    def get_queryset(self):
        today = datetime.now().date()
        return Visitor.objects.filter(last_visit__date=today).order_by('-last_visit')
