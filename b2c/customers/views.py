from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import CustomerSerializer
from rest_framework.generics import DestroyAPIView

User = get_user_model()


class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "name",                     
        "user_profile__contact_email",
        "user_profile__phone_number",
        "user_profile__address",
    ]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    def get_queryset(self):
        return User.objects.select_related("user_profile").all()


class CustomerDetailView(generics.RetrieveAPIView):
    queryset = User.objects.select_related("user_profile").all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"


class CustomerDeleteView(generics.DestroyAPIView):
    queryset = User.objects.select_related("user_profile").all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Customer deleted successfully."}, status=status.HTTP_200_OK)


