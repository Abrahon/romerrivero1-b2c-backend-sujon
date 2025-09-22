from django.urls import path
from .views import (
    # ===== Admin Category =====
    AdminCategoryListCreateView,
    AdminCategoryRetrieveUpdateDeleteView,
    AdminCategoryBulkDeleteView,

    # ===== Admin Product =====
    AdminProductListCreateView,
    AdminProductRetrieveUpdateDeleteView,
    AdminProductBulkDelete,
    AdminProductStatusListView,
    BulkUploadProductView,

    # ===== User Views =====
    UserCategoryListView,
    UserCategoryProductListView,
    UserProductListView,
    UserProductDetailView,
    UserProductSearchView,

    # ===== Public / Filter =====
    CategoryProductFilterView,
    ProductSearchFilterView,
    TopProductsView,
    LimitedDealsProductListView


    
)

urlpatterns = [
    # Admin Category URLs
    # ---------------------
    path('admin/categories/', AdminCategoryListCreateView.as_view(), name='admin-category-list-create'),
    path('admin/categories/<int:id>/', AdminCategoryRetrieveUpdateDeleteView.as_view(), name='admin-category-rud'),
    path('admin/categories/bulk-delete/', AdminCategoryBulkDeleteView.as_view(), name='admin-category-bulk-delete'),

    # Admin Product URLs
    # ---------------------
    path('admin/products/', AdminProductListCreateView.as_view(), name='admin-product-list-create'),
    path('admin/products/<int:id>/', AdminProductRetrieveUpdateDeleteView.as_view(), name='admin-product-rud'),
    path('admin/products/bulk-delete/', AdminProductBulkDelete.as_view(), name='admin-product-bulk-delete'),
    path('admin/products/status/', AdminProductStatusListView.as_view(), name='admin-product-status-list'),
    path('admin/products/bulk-upload/', BulkUploadProductView.as_view(), name='admin-product-bulk-upload'),

    # User URLs (Authenticated)
    # ---------------------
    path('user/categories/', UserCategoryListView.as_view(), name='user-category-list'),
    path('user/categories/<int:category_id>/products/', UserCategoryProductListView.as_view(), name='user-category-products'),
    path('user/products/', UserProductListView.as_view(), name='user-product-list'),
    path('user/products/<int:id>/', UserProductDetailView.as_view(), name='user-product-detail'),
    path('user/products/search/', UserProductSearchView.as_view(), name='user-product-search'),


    # Public / Filter / Search
    # ---------------------
    path("products/top/", TopProductsView.as_view(), name="top-products"),
    path("products/limited-deals/", LimitedDealsProductListView.as_view(), name="limited-deals-products"),
    path('products/filter/', CategoryProductFilterView.as_view(), name='category-product-filter'),
    path('products/search/', ProductSearchFilterView.as_view(), name='product-search-filter'),
]
