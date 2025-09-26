from django.urls import path
from .views import (
    CouponListCreateView, 
    CouponRetrieveUpdateDestroyView, 
    ApplyCouponView
)

urlpatterns = [
    # Admin URLs
    path('admin/coupons/', CouponListCreateView.as_view(), name='admin-coupons-list-create'),
    path('admin/coupons/<int:id>/', CouponRetrieveUpdateDestroyView.as_view(), name='admin-coupons-detail'),

    # User URL to apply coupon
    path('coupons/apply/', ApplyCouponView.as_view(), name='apply-coupon'),
]

