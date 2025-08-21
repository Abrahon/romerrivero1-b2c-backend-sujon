# b2c/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    path('products/', views.ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),
    path('products/bulk-upload/',views. BulkUploadProductView.as_view(), name='bulk-product-upload'),

    #wishlist 
    path("wishlist/", views. WishlistListCreateView.as_view(), name="wishlist-list-create"),
    path("my_wishlist/",views. MyWishlistView.as_view(), name="my-wishlist"),
    path("wishlist/remove/",views. WishlistDeleteView.as_view(), name="wishlist-remove")
]


