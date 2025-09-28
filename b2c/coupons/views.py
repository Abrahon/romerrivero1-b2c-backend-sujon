
# from rest_framework import generics, permissions, status, serializers
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .models import Coupon, CouponRedemption
# from .serializers import CouponSerializer, ApplyCouponSerializer
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from decimal import Decimal
# from .serializers import ApplyCouponSerializer
# from b2c.products.models import Products

# # ---------------- Admin Coupon Management ----------------
# class CouponListCreateView(generics.ListCreateAPIView):
#     queryset = Coupon.objects.all()
#     serializer_class = CouponSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def perform_create(self, serializer):
#         # Ensure only one coupon per product/category exists
#         product = serializer.validated_data.get('product')
#         category = serializer.validated_data.get('category')

#         if product and Coupon.objects.filter(product=product).exists():
#             raise serializers.ValidationError(f"Coupon for product {product.title} already exists.")
#         if category and Coupon.objects.filter(category=category).exists():
#             raise serializers.ValidationError(f"Coupon for category {category.name} already exists.")

#         serializer.save()


# class CouponRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Coupon.objects.all()
#     serializer_class = CouponSerializer
#     permission_classes = [permissions.IsAdminUser]
#     lookup_field = "id"



# class ApplyCouponView(generics.GenericAPIView):
#     serializer_class = ApplyCouponSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         coupon = serializer.validated_data['coupon']
#         product_id = serializer.validated_data.get('product_id')

#         # Fetch product price automatically
#         if product_id:
#             try:
#                 product = Products.objects.get(id=product_id)
#             except Products.DoesNotExist:
#                 return Response({"error": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)
#             total_amount = product.price
#         else:
#             return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Calculate discount
#         discount_amount = (total_amount * Decimal(coupon.discount_percentage)) / Decimal("100")
#         final_amount = total_amount - discount_amount

#         # Record redemption
#         CouponRedemption.objects.get_or_create(coupon=coupon, user=request.user)

#         return Response({
#             "message": f"Coupon applied successfully! you get {coupon.discount_percentage}% discount.",
#             "discount_percentage": coupon.discount_percentage,
#             "discounted_amount": str(discount_amount),
#             "final_amount": str(final_amount),
#         }, status=status.HTTP_200_OK)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Coupon, CouponRedemption
from .serializers import CouponSerializer, ApplyCouponSerializer
from b2c.products.models import Products
from decimal import Decimal
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ApplyCouponSerializer
from b2c.products.models import Products
from .models import CouponRedemption

# ---------------- Admin Coupon Management ----------------
class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()  # Admin can create coupon for products/categories


class CouponRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": "Coupon updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "success": "Coupon deleted successfully"
        }, status=status.HTTP_200_OK)



# class ApplyCouponView(generics.GenericAPIView):
#     serializer_class = ApplyCouponSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         coupon = serializer.validated_data["coupon"]
#         products = serializer.validated_data["products"]

#         # ✅ Calculate total price of all selected products
#         total_amount = sum([p.price for p in products])

#         # ✅ Calculate discount
#         if coupon.discount_type == "percentage":
#             discount_amount = (total_amount * Decimal(coupon.discount_value)) / Decimal("100")
#         else:  # fixed discount
#             discount_amount = Decimal(coupon.discount_value)

#         final_amount = total_amount - discount_amount
#         if final_amount < 0:
#             final_amount = Decimal("0.00")

#         # ✅ Record redemption (avoid duplicate per user)
#         CouponRedemption.objects.get_or_create(coupon=coupon, user=request.user)

#         return Response({
#             "message": f"Coupon applied successfully! You get {coupon.discount_value} {coupon.discount_type} discount.",
#             "discount_type": coupon.discount_type,
#             "discount_value": str(coupon.discount_value),
#             "total_amount": str(total_amount),
#             "discounted_amount": str(discount_amount),
#             "final_amount": str(final_amount),
#             "applied_products": [p.id for p in products],
#         }, status=status.HTTP_200_OK)
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ApplyCouponSerializer
from .models import CouponRedemption

class ApplyCouponView(generics.GenericAPIView):
    serializer_class = ApplyCouponSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data["coupon"]
        products = serializer.validated_data["products"]

        # ✅ Calculate total price using discounted_price of each product
        total_amount = sum([p.discounted_price for p in products])

        # ✅ Calculate coupon discount
        if coupon.discount_type == "percentage":
            discount_amount = (total_amount * Decimal(coupon.discount_value)) / Decimal("100")
        else:  # fixed discount
            discount_amount = Decimal(coupon.discount_value)

        # ✅ Final amount after applying coupon
        final_amount = total_amount - discount_amount
        if final_amount < 0:
            final_amount = Decimal("0.00")

        # ✅ Record redemption (avoid duplicate per user)
        CouponRedemption.objects.get_or_create(coupon=coupon, user=request.user)

        return Response({
            "message": f"Coupon applied successfully! You get {coupon.discount_value} {coupon.discount_type} discount.",
            "discount_type": coupon.discount_type,
            "discount_value": str(coupon.discount_value),
            "total_amount": str(total_amount),           # Total discounted price
            "discounted_amount": str(discount_amount),  # Coupon discount
            "final_amount": str(final_amount),
            "applied_products": [p.id for p in products],
        }, status=status.HTTP_200_OK)
