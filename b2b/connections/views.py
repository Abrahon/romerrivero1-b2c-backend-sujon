from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Connection
from .serializers import ConnectionSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class ConnectionListCreateView(generics.ListCreateAPIView):
    """
    List all connections or create a new connection
    """
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        return serializer.save()


class ConnectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a connection
    """
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAdminUser] 
    def delete(self, request, *args, **kwargs):
        """
        This method handles the DELETE request to delete a connection.
        """
        instance = self.get_object()  
        self.perform_destroy(instance) 
        return Response({"detail": "Connection deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """
        This method actually deletes the instance from the database.
        """
        instance.delete()
