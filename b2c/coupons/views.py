
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Coupon, CouponRedemption
from .serializers import CouponSerializer, ApplyCouponSerializer
from b2c.products.models import Products

# ------------------------------
# Admin: List and Create Coupons
# ------------------------------
class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


# ------------------------------
# Admin: Retrieve, Update, Delete
# ------------------------------
class CouponRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'


# ------------------------------
# User: Apply Coupon
# ------------------------------
class ApplyCouponView(generics.GenericAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        product_id = serializer.validated_data.get('product_id')

        coupon = get_object_or_404(Coupon, code=code, active=True)

        # Check redemption
        if CouponRedemption.objects.filter(coupon=coupon, user=request.user).exists():
            return Response(
                {"error": "You have already used this coupon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check product eligibility
        if coupon.product and coupon.product.id != product_id:
            return Response(
                {"error": "This coupon is not valid for this product."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check category eligibility
        if coupon.category and product_id:
            product = get_object_or_404(Product, id=product_id)
            if product.category != coupon.category:
                return Response(
                    {"error": "This coupon is not valid for this category."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Redeem coupon
        CouponRedemption.objects.create(coupon=coupon, user=request.user)

        return Response({
            "message": f"Coupon applied successfully! {coupon.discount_percentage}% discount.",
            "coupon": CouponSerializer(coupon).data
        }, status=status.HTTP_200_OK)
