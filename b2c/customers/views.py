from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import CustomerSerializer
from rest_framework.generics import DestroyAPIView
from b2c.orders.models import Order
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
        # ✅ Only users who have at least one order
        return (
            User.objects.filter(orders__isnull=False)  # only users with orders
            .select_related("user_profile")
            .distinct()  # avoid duplicates if multiple orders
        )



class CustomerDetailView(generics.RetrieveAPIView):
    queryset = User.objects.select_related("user_profile").all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"


# class CustomerDeleteView(generics.DestroyAPIView):
#     queryset = User.objects.select_related("user_profile").all()
#     serializer_class = CustomerSerializer
#     permission_classes = [permissions.IsAdminUser]
#     lookup_field = "id"

#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response({"detail": "Customer deleted successfully."}, status=status.HTTP_200_OK)
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response


class CustomerDeleteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all orders for this user
        orders = Order.objects.filter(user_id=user_id)

        if not orders.exists():
            return Response({"detail": "No orders found for this user"}, status=status.HTTP_404_NOT_FOUND)

        # Clear customer info in each order
        orders.update(
            customer_name="Deleted",
            customer_email="deleted@example.com",
            shipping_address=""
        )

        return Response(
            {"detail": f"Customer info for {orders.count()} order(s) has been deleted."},
            status=status.HTTP_200_OK
        )


