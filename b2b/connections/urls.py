from .views import ConnectionListCreateView,ConnectionDetailView
from django.urls import path

urlpatterns = [
    path('connections/', ConnectionListCreateView.as_view(), name='connection-list-create'),
    path('connections/<int:pk>/', ConnectionDetailView.as_view(), name='connection-detail'),
]
