from django.urls import path
from .views import (
   
    # Admin URLs
    AdminCategoryListCreateView,
    AdminCategoryProductListView,
    AdminProductListCreateView,
    AdminProductRetrieveUpdateDeleteView,
    AdminProductBulkDelete,
    AdminProductStatusListView,
    BulkUploadProductView,
    # Authenticated User URLs
    UserCategoryListView,
    UserCategoryProductListView,
    UserProductListView,
    UserProductDetailView,
    UserProductSearchView,
    CategoryProductFilterView
)

urlpatterns = [

    # =========================
    # ADMIN ROUTES
    # =========================
    path('admin/categories/', AdminCategoryListCreateView.as_view(), name='admin-category-list-create'),
    # path('admin/categories/<uuid:category_id>/products/', AdminCategoryProductListView.as_view(), name='admin-category-products'),
    path('admin/categories/<int:category_id>/products/', AdminCategoryProductListView.as_view(), name='admin-category-products'),
    path('admin/products/', AdminProductListCreateView.as_view(), name='admin-product-list-create'),
    # path('admin/products/<uuid:id>/', AdminProductRetrieveUpdateDeleteView.as_view(), name='admin-product-detail'),
    path('admin/products/<int:id>/', AdminProductRetrieveUpdateDeleteView.as_view(), name='admin-product-detail'),
    path('admin/products/bulk-delete/', AdminProductBulkDelete.as_view(), name='admin-product-bulk-delete'),
    path('admin/products/status/', AdminProductStatusListView.as_view(), name='admin-product-status'),
    path('admin/products/bulk-upload/', BulkUploadProductView.as_view(), name='admin-product-bulk-upload'),


    # =========================
    # AUTHENTICATED USER ROUTES
    # =========================
    path('categories/', UserCategoryListView.as_view(), name='user-category-list'),
    path('categories/<uuid:category_id>/products/', UserCategoryProductListView.as_view(), name='user-category-products'),
    path('products/', UserProductListView.as_view(), name='user-product-list'),
    path('products/<int:id>/', UserProductDetailView.as_view(), name='user-product-detail'),
    path('products/search/', UserProductSearchView.as_view(), name='user-product-search'),
    path('products/category-filter/', CategoryProductFilterView.as_view(), name='category-product-filter'),
]

