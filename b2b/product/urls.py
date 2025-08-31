
from django.urls import path
from .views import ProductListView, ProductDetailView, AdminProductCreateUpdateDeleteView,BulkUploadProductView,AdminProductListCreateView,AdminCategoryListCreateView

urlpatterns = [
    # Admin Views (CRUD actions for products)
     path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-category-list-create"),
    path('admin/products/<int:pk>/', AdminProductCreateUpdateDeleteView.as_view(), name='admin-product-detail'),
    path('admin/products/', AdminProductListCreateView.as_view(), name='admin-product-create'),

    # User Views (View product list and details)
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/bulk-upload/', BulkUploadProductView.as_view(), name='bulk-product-upload'),
]
