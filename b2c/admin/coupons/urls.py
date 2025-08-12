# b2c/admin/coupons/urls.py
from django.urls import path
from .views import CouponListView, CouponDetailView

urlpatterns = [
    path('coupon/', CouponListView.as_view(), name='coupon-list-create'),
    path('coupon/<int:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
    # path('apply-coupon/', ApplyCouponView.as_view(), name='apply-coupon'),
]
