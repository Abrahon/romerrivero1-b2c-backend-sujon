from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import Promotion
from .serializers import PromotionSerializer

class PromotionListView(generics.ListAPIView):
    """
    List all active promotions (for users)
    """
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = []  # Open to all users

class PromotionAdminListCreateView(generics.ListCreateAPIView):
    """
    Admin: List all promotions or create a new promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promotion = serializer.save()
        return Response({
            "message": "Promotion added successfully.",
            "promotion": serializer.data
        }, status=status.HTTP_201_CREATED)

class PromotionRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin: Retrieve, update, or delete a promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"message": "Promotion deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
