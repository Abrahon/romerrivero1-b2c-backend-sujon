from django.urls import path
from .views import DashboardOverview,AnalyticsView


urlpatterns = [
    path('dashboard/overview/', DashboardOverview.as_view(), name='dashboard-overview'),
     path("dashboard/analytics/", AnalyticsView.as_view(), name="analytics"),
]


