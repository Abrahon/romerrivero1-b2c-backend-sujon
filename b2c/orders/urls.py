from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    PlaceOrderView,
    OrderTrackingView,
    BuyNowView,
)

urlpatterns = [
    # List all orders for logged-in user
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    # Place order from cart
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    # Track an order (by ID or order_number)
    path("orders/<str:order_identifier>/track/", OrderTrackingView.as_view(), name="order-tracking"),
    # Buy Now (direct checkout for single product)
    path("orders/buy-now/", BuyNowView.as_view(), name="buy-now"),
]
