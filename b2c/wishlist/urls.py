from django.urls import path
from .views import WishlistListCreateView, WishlistRemoveView

urlpatterns = [
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist-list-create'),
    path("wishlist/remove/<int:product_id>/", WishlistRemoveView.as_view(), name="wishlist-remove")
]
