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
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ApplyCouponSerializer
from b2c.coupons.models import CouponRedemption

# ---------------- Admin Coupon Management ----------------
class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save() 


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

#         #  Calculate total price considering product discount if available
#         total_amount = Decimal("0.00")
#         for p in products:
#             product_price = getattr(p, "discounted_price", None) or p.price
#             total_amount += Decimal(product_price)

#         # ✅ Calculate discount based on coupon type
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
#             "coupon_discount_value": str(discount_amount),  
#             "total_amount": str(total_amount),
#             "final_amount": str(final_amount),
#             "applied_products": [p.id for p in products],
#         }, status=status.HTTP_200_OK)


# coupon disccount logic for multiple products an dqunatity



class ApplyCouponView(generics.GenericAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data["coupon"]
        products = serializer.validated_data["products"]
        product_quantities = serializer.validated_data["product_quantities"]

        total_amount = Decimal("0.00")

        # 🟩 FIX: loop through ALL products and use correct price * quantity
        product_list = []
        for p in products:
            product_price = getattr(p, "discounted_price", None) or p.price
            print("product price",product_price)
            quantity = Decimal(product_quantities.get(p.id, 1))
            print("quantity",quantity)
            subtotal = Decimal(product_price) * quantity
            print("subtotal",subtotal)
            total_amount += subtotal

            # 🟩 include full product info in response
            product_list.append({
                "id": p.id,
                "title": p.title,
                "price": str(product_price),
                "quantity": int(quantity),
                "subtotal": str(subtotal)
            })

        # 🟩 FIX: Apply correct discount
        if coupon.discount_type == "percentage":
            discount_amount = (total_amount * Decimal(coupon.discount_value)) / Decimal("100")
            print("discount amount",discount_amount)
        else:
            discount_amount = Decimal(coupon.discount_value)
            print("discount amount",discount_amount)

        final_amount = max(total_amount - discount_amount, Decimal("0.00"))
        print("final amount",final_amount)              

        CouponRedemption.objects.get_or_create(coupon=coupon, user=request.user)

        return Response({
            "message": f"Coupon applied successfully! You get {coupon.discount_value} {coupon.discount_type} discount.",
            "discount_type": coupon.discount_type,
            "coupon_discount_value": str(discount_amount),
            "total_amount": str(total_amount),
            "final_amount": str(final_amount),
            "applied_products": product_list,
        }, status=status.HTTP_200_OK)
