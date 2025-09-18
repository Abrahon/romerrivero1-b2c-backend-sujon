from django.urls import path
from .views import CartItemListCreateView, CartItemUpdateDeleteView

urlpatterns = [
    path('cart/', CartItemListCreateView.as_view(), name='cart-list-create'),
    path('cart/<int:id>/', CartItemUpdateDeleteView.as_view(), name='cart-update-delete'),
]

