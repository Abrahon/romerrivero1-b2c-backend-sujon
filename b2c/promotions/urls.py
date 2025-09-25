from django.urls import path
from .views import HeroPromotionView, HeroPromotionsView

urlpatterns = [
    path("hero-promotion/", HeroPromotionView.as_view(), name="hero-promotion"),
    path("hero-promotions/", HeroPromotionsView.as_view(), name="hero-promotions"),
]
