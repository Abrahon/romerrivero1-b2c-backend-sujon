# visitors/urls.py
from django.urls import path
from .views import VisitorListView, TodayVisitorsView

urlpatterns = [
    path('', VisitorListView.as_view(), name='visitors-list'),
    path('today/', TodayVisitorsView.as_view(), name='visitors-today'),
]
