from django.urls import path
from .views import (
    UserGrowthView,
    OrderStatusDistributionView,
    TopSellingProductsView,
    CustomerSegmentationView,
    CustomerByLocationView,
    OrderStatisticsView,
)

urlpatterns = [
    path('user-growth/', UserGrowthView.as_view(), name='user-growth'),
    path('order-status-distribution/', OrderStatusDistributionView.as_view(), name='order-status-distribution'),
    path('top-selling-products/', TopSellingProductsView.as_view(), name='top-selling-products'),
    path('customer-segmentation/', CustomerSegmentationView.as_view(), name='customer-segmentation'), 
    path('customer-by-location/', CustomerByLocationView.as_view(), name='customer-by-location'),
    path('order-statistics/', OrderStatisticsView.as_view(), name='order-statistics'),
]
    