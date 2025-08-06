from django.urls import path
from .views import OrderSummaryView, PlaceOrderView

urlpatterns = [
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('place/', PlaceOrderView.as_view(), name='order-place'),
]
