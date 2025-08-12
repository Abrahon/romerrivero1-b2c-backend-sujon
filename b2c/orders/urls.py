

# from django.urls import path
# from .views import OrderListView, OrderSummaryView, PlaceOrderView

# urlpatterns = [
#     path('', OrderListView.as_view(), name='order-list'),
#     path('summary/', OrderSummaryView.as_view(), name='order-summary'),
#     path('place/', PlaceOrderView.as_view(), name='place-order'),
# ]
# b2c/orders/urls.py

# b2c/orders/urls.py

from django.urls import path
from .views import OrderListView, OrderDetailView, PlaceOrderView

urlpatterns = [
    # List user's orders (order history screen)
    path('', OrderListView.as_view(), name='order-list'),
    
    # Detailed order (items + metadata)
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    
    # Place an order from the cart
    path('place/', PlaceOrderView.as_view(), name='place-order'),
]

