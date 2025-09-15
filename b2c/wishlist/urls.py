from django.urls import path
from .views import WishlistListCreateView, WishlistRemoveView

urlpatterns = [
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist-list-create'),
    path('wishlist/<int:item_id>/delete/', WishlistRemoveView.as_view(), name='wishlist-remove'),
]
