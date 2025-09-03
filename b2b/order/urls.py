from django.urls import path
from .views import OrderCreateView, OrderDetailView, OrderListView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),  # Admin view all orders
    path('orders/create/', OrderCreateView.as_view(), name='order-create'), 
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  
]