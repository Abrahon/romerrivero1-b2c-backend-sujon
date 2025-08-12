# support/urls.py
from django.urls import path
from .views import SupportRequestCreateView

urlpatterns = [
    path('support/', SupportRequestCreateView.as_view(), name='support-create'),
]
