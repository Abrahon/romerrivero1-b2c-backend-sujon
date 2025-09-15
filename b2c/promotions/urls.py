from django.urls import path
from .views import (
    PromotionListView,
    PromotionAdminListCreateView,
    PromotionRetrieveUpdateDeleteView
)

urlpatterns = [
    path('list/', PromotionListView.as_view(), name='promotion-list'),
    path('admin/promotion/', PromotionAdminListCreateView.as_view(), name='promotion-admin-list-create'),
    path('admin/promotion/<int:id>/', PromotionRetrieveUpdateDeleteView.as_view(), name='promotion-admin-detail'),
]
