from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    PlaceOrderView,
    BuyNowView,
    AdminOrderListView,
    OrderTrackingView,
    OrderTrackingView,
    OrderListFilter,
    # OrderTrackingDetailView,
    AdminUpdateOrderStatusView,
    OrderDeleteView
)

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    path("orders/tracking/<str:order_identifier>/", OrderTrackingView.as_view(), name="order-tracking"),
    path("orders/buy-now/", BuyNowView.as_view(), name="buy-now"),
    # path('admin/order/status/', OrderListFilter.as_view(), name='order-list-filter'),

    #  path("orders/tracking/", OrderTrackingView.as_view(), name="tracking-list-create"),
    # path("orders/tracking/<int:pk>/", OrderTrackingDetailView.as_view(), name="tracking-detail"),
    path("admin/orders/<int:id>/status/", AdminUpdateOrderStatusView.as_view(), name="admin_update_order_status"),
    path('admin/orders/status/', OrderListFilter.as_view(), name='order-list'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='admin-order-delete'),
]
