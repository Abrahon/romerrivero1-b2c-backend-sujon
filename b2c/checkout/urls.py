from django.urls import path
from .views import ShippingListCreateView

urlpatterns = [
    path('shipping/', ShippingListCreateView.as_view(), name='shipping-list-create'),
]
