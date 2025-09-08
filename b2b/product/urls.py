
from django.urls import path
from .views import ProductListView, ProductDetailView, AdminProductCreateUpdateDeleteView,BulkUploadProductView,AdminProductListCreateView,AdminCategoryListCreateView,ProductSearchFilterView,AdminProductBulkDelete,StatusProductAPIView,AdminCategoryProductListView,UserCategoryProductListView


urlpatterns = [
    path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-category-list-create"),

    path("admin/products/<uuid:id>/", AdminProductCreateUpdateDeleteView.as_view(), name="admin-product-detail"),
    path("admin/products/", AdminProductListCreateView.as_view(), name="admin-product-create"),
    path("admin/products/bulk_delete/", AdminProductBulkDelete.as_view(), name="admin-product-bulk-delete"),
    path("admin/products/status/", StatusProductAPIView.as_view(), name="admin-status-product-list"),
    path('admin/products/category/<uuid:category_id>/', AdminCategoryProductListView.as_view(), name='admin-category-product-list'),

    # User Views
    path('products/search/', ProductSearchFilterView.as_view(), name='product-search'),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<uuid:id>/", ProductDetailView.as_view(), name="product-detail"),
    path('products/category/<uuid:category_id>/', UserCategoryProductListView.as_view(), name='user-category-product-list'),
    path("products/bulk_upload/", BulkUploadProductView.as_view(), name="bulk-product-upload"),
]

