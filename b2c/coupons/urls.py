# b2c/coupons/urls.py
from django.urls import path
from .views import CouponListCreateView, CouponDetailView

urlpatterns = [
    path("coupons/", CouponListCreateView.as_view(), name="coupon-list-create"),
    path("coupons/<int:pk>/", CouponDetailView.as_view(), name="coupon-detail"),
]
