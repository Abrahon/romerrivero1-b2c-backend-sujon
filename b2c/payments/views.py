from django.shortcuts import render
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from b2c.orders.models import Order
from rest_framework.permissions import AllowAny

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentIntentView(APIView):
    
    def post(self,request, *args, **kwargs):
        order_id = request.data.get('order_id')
        order = Order.objects.get(id=order_id)

        intent = stripe.PaymentIntent.create(
            amount=int(order.amount * 100),  # amount in cents
            currency='usd',
            metadata={'order_id': order.id}
        ) 

        order.stripe_payment_intent = intent.id
        order.save()

        return Response({
            'client_secret': intent.client_secret,
            'payment_intent': intent.id
        })
    permission_classes = [AllowAny]
    


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle successful payment
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent['metadata']['order_id']
        order = Order.objects.get(id=order_id)
        order.is_paid = True
        order.payment_status = 'success'
        order.save()

    # Handle failed payment
    if event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        order_id = intent['metadata']['order_id']
        order = Order.objects.get(id=order_id)
        order.is_paid = False
        order.payment_status = 'failed'
        order.save()

    return HttpResponse(status=200)



