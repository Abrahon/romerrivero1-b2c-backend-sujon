from django.urls import path
from .views import (
    CouponListCreateView, 
    CouponRetrieveUpdateDeleteView, 
    ApplyCouponView
)

urlpatterns = [
    # Admin URLs
    path('admin/coupons/', CouponListCreateView.as_view(), name='admin-coupons-list-create'),
    path('admin/coupons/<int:id>/', CouponRetrieveUpdateDeleteView.as_view(), name='admin-coupons-detail'),

    # User URL to apply coupon
    path('coupons/apply/', ApplyCouponView.as_view(), name='apply-coupon'),
]

# from django.urls import path
# from .views import CouponAdminView, ApplyCouponView

# urlpatterns = [
#     # Admin URLs
#     path('admin/coupons/', CouponAdminView.as_view({'get': 'list', 'post': 'create'}), name='admin-coupons-list-create'),
#     path('admin/coupons/<int:pk>/', CouponAdminView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='admin-coupons-detail'),

#     # User URL to apply coupon
#     path('coupons/apply/', ApplyCouponView.as_view(), name='apply-coupon'),
# ]
