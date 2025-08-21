from django.urls import path
from .views import OrderCreateView, OrderDetailView, OrderListView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),  # Admin view all orders
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),  # User creates an order
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  # Admin read, update, delete an order
]
