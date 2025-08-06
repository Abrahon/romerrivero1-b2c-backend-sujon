from django.urls import path
from .views import StripePaymentIntentView, stripe_webhook

urlpatterns = [
    path('create-intent/', StripePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
