from django.urls import path
from .views import CartItemListCreateView, CartItemUpdateDeleteView

urlpatterns = [
    path('', CartItemListCreateView.as_view(), name='cart-list-create'),
    path('<int:pk>/', CartItemUpdateDeleteView.as_view(), name='cart-update-delete'),
]
