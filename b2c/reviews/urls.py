from django.urls import path
from .views import ReviewListCreateAPIView, ReviewUpdateAPIView, ReviewDeleteAPIView

urlpatterns = [
    # List and create reviews for a product
    path('product/<int:product_id>/reviews/', ReviewListCreateAPIView.as_view(), name='product-reviews'),
    path('reviews/<int:pk>/update/', ReviewUpdateAPIView.as_view(), name='review-update'),
    path('reviews/<int:pk>/delete/', ReviewDeleteAPIView.as_view(), name='review-delete'),
]
