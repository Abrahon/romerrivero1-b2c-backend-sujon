from django.urls import path
from .views import ContactMessageCreateAPIView

urlpatterns = [
    path("contact-now/", ContactMessageCreateAPIView.as_view(), name="contact-now"),
]
