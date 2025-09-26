
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Coupon, CouponRedemption
from .serializers import CouponSerializer, ApplyCouponSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from decimal import Decimal
from .serializers import ApplyCouponSerializer
from b2c.products.models import Products

# ---------------- Admin Coupon Management ----------------
class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # Ensure only one coupon per product/category exists
        product = serializer.validated_data.get('product')
        category = serializer.validated_data.get('category')

        if product and Coupon.objects.filter(product=product).exists():
            raise serializers.ValidationError(f"Coupon for product {product.title} already exists.")
        if category and Coupon.objects.filter(category=category).exists():
            raise serializers.ValidationError(f"Coupon for category {category.name} already exists.")

        serializer.save()


class CouponRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"



class ApplyCouponView(generics.GenericAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.validated_data['coupon']
        product_id = serializer.validated_data.get('product_id')

        # Fetch product price automatically
        if product_id:
            try:
                product = Products.objects.get(id=product_id)
            except Products.DoesNotExist:
                return Response({"error": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            total_amount = product.price
        else:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate discount
        discount_amount = (total_amount * Decimal(coupon.discount_percentage)) / Decimal("100")
        final_amount = total_amount - discount_amount

        # Record redemption
        CouponRedemption.objects.get_or_create(coupon=coupon, user=request.user)

        return Response({
            "message": f"Coupon applied successfully! you get {coupon.discount_percentage}% discount.",
            "discount_percentage": coupon.discount_percentage,
            "discounted_amount": str(discount_amount),
            "final_amount": str(final_amount),
        }, status=status.HTTP_200_OK)
