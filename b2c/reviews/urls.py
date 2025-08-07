from django.urls import path
from .views import ReviewListCreateAPIView, ReviewDeleteAPIView

urlpatterns = [
    path('products/<int:product_id>/reviews/', ReviewListCreateAPIView.as_view(), name='product-reviews'),
    path('reviews/<int:pk>/delete/', ReviewDeleteAPIView.as_view(), name='review-delete'),
]
