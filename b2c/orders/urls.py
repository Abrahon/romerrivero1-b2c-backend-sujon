from django.urls import path
from .views import OrderSummaryView, PlaceOrderView,CreateOrderView

urlpatterns = [
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('place/', PlaceOrderView.as_view(), name='order-place'),
    path('create/', CreateOrderView.as_view(), name='create-order'),
]
