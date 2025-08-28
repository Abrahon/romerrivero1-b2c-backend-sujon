
from django.urls import path
from .views import AdminCustomerCreateView, AdminCustomerDetailView

urlpatterns = [
    path('customers/', AdminCustomerCreateView.as_view(), name='create-customer'), 
    path('customers/<int:pk>/', AdminCustomerDetailView.as_view(), name='customer-detail'),  
]
