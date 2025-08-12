from django.shortcuts import render

# Create your views here.
# b2c/admin/coupons/views.py
from rest_framework import generics
from .models import Coupon
from .serializers import CouponSerializer
# from accounts .permissions import IsAdminUser
from rest_framework.permissions import AllowAny


class CouponListView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]
