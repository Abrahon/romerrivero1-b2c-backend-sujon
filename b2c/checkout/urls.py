from django.urls import path
from .views import ShippingListCreateView, ShippingRetrieveUpdateDeleteView


urlpatterns = [
    path('shipping/', ShippingListCreateView.as_view(), name='shipping-list-create'),
    path('shipping/<int:id>/', ShippingRetrieveUpdateDeleteView.as_view(), name='shipping-detail'),
]
