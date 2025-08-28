from django.urls import path
from .views import InquiryListCreateView, InquiryUpdateDeleteView

urlpatterns = [
    path('inquiries/', InquiryListCreateView.as_view(), name='inquiry-list-create'),
    path('inquiries/<int:pk>/', InquiryUpdateDeleteView.as_view(), name='inquiry-update-delete'),
]
