from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            notifications = Notification.objects.filter(user=request.user)
        else:
            notifications = Notification.objects.none()  # No results for guests
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
