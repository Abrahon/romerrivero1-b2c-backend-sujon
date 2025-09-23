from django.urls import path
from .views import CustomerListView, CustomerDetailView, CustomerDeleteView

urlpatterns = [
    path("customers/", CustomerListView.as_view(), name="customer-list"),
    path("customers/<int:id>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("customers/<int:id>/delete/", CustomerDeleteView.as_view(), name="customer-delete"),
]
