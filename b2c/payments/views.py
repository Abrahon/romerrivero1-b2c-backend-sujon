# from django.shortcuts import render
# import stripe
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from b2c.orders.models import Order
# from rest_framework.permissions import AllowAny

# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# import json

# # Create your views here.
# stripe.api_key = settings.STRIPE_SECRET_KEY

# class StripePaymentIntentView(APIView):
    
#     def post(self,request, *args, **kwargs):
#         order_id = request.data.get('order_id')
#         order = Order.objects.get(id=order_id)

#         intent = stripe.PaymentIntent.create(
#             amount=int(order.total_amount * 100),  # amount in cents
#             currency='usd',
#             metadata={'order_id': order.id}
#         ) 

#         order.stripe_payment_intent = intent.id
#         order.save()

#         return Response({
#             'client_secret': intent.client_secret,
#             'payment_intent': intent.id
#         })
#     permission_classes = [AllowAny]
    


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError:
#         return HttpResponse(status=400)

#     # Handle successful payment
#     if event['type'] == 'payment_intent.succeeded':
#         intent = event['data']['object']
#         order_id = intent['metadata']['order_id']
#         order = Order.objects.get(id=order_id)
#         order.is_paid = True
#         order.payment_status = 'success'
#         order.save()

#     # Handle failed payment
#     if event['type'] == 'payment_intent.payment_failed':
#         intent = event['data']['object']
#         order_id = intent['metadata']['order_id']
#         order = Order.objects.get(id=order_id)
#         order.is_paid = False
#         order.payment_status = 'failed'
#         order.save()

#     return HttpResponse(status=200)

import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from b2c.orders.models import Order
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponse
import json
from django.db import transaction
# Set the Stripe secret key from settings   
stripe.api_key = settings.STRIPE_SECRET_KEY



# class StripePaymentIntentView(APIView):
#     """
#     Creates a PaymentIntent for Stripe to handle payments.
#     This view is called when the user proceeds to checkout.
#     """
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get('order_id')
        
#         # Ensure that the order exists
#         try:
#             order = Order.objects.get(id=order_id)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found."}, status=404)

#         # Ensure the amount is greater than the minimum charge amount for Stripe
#         if order.total_amount < 0.5:  # Minimum charge for USD is $0.50
#             return Response({"error": "Amount is too low. The minimum charge for this currency is $0.50."}, status=400)

#         # Create a PaymentIntent with Stripe
#         try:
#             intent = stripe.PaymentIntent.create(
#                 amount=int(order.total_amount * 100),  # Convert to cents
#                 currency='usd',
#                 metadata={'order_id': order.id}  # Pass the order ID as metadata
#             )
#         except stripe.error.InvalidRequestError as e:
#             return Response({"error": str(e)}, status=400)

#         # Save the payment intent ID to the order
#         order.stripe_payment_intent = intent.id
#         order.save()

#         # Return the client secret to the frontend
#         return Response({
#             'client_secret': intent.client_secret,
#             'payment_intent': intent.id
#         })




# Set your secret key (ensure it is in your settings file)
# stripe.api_key = settings.STRIPE_SECRET_KEY

# class StripePaymentIntentView(APIView):
    
#     def post(self, request, *args, **kwargs):
#         # Get the order ID from the request data
#         order_id = request.data.get('order_id')
        
#         # Retrieve the order from the database using the provided order_id
#         order = Order.objects.get(id=order_id)

#         # Convert the order amount to cents (Stripe requires the amount in cents)
#         amount_in_cents = int(order.total_amount * 100)  # Convert to cents

#         # Ensure the amount is greater than or equal to $0.50
#         minimum_amount = 50  # The minimum charge in cents (i.e., $0.50)
        
#         if amount_in_cents < minimum_amount:
#             return Response({
#                 'error': 'Amount is too low. The minimum charge for this currency is $0.50.'
#             }, status=400)
        
#         # Create the PaymentIntent with the valid amount
#         try:
#             intent = stripe.PaymentIntent.create(
#                 amount=amount_in_cents,  # Amount in cents
#                 currency='usd',  # Currency to be used for the transaction
#                 metadata={'order_id': order.id}  # Store the order ID in metadata
#             ) 

#             # Save the payment intent ID in the order
#             order.stripe_payment_intent = intent.id
#             order.save()

#             # Return the client secret to the frontend so the user can complete the payment
#             return Response({
#                 'client_secret': intent.client_secret,
#                 'payment_intent': intent.id
#             })
        
#         except stripe.error.StripeError as e:
#             # Handle Stripe API errors
#             return Response({
#                 'error': str(e)
#             }, status=400)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from b2c.orders.models import Order
import stripe

# Set your secret key (ensure it is in your settings file)
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentIntentView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Get the order ID from the request data
        order_id = request.data.get('order_id')
        
        # Retrieve the order from the database using the provided order_id
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        # Convert the order amount to cents (Stripe requires the amount in cents)
        amount_in_cents = int(order.total_amount * 100)  # Convert to cents

        # Ensure the amount is greater than or equal to $0.50
        minimum_amount = 50  # The minimum charge in cents (i.e., $0.50)
        
        if amount_in_cents < minimum_amount:
            return Response({
                'error': 'Amount is too low. The minimum charge for this currency is $0.50.'
            }, status=400)
        
        # Create the PaymentIntent with the valid amount
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,  # Amount in cents
                currency='usd',  # Currency to be used for the transaction
                metadata={'order_id': order.id}  # Store the order ID in metadata
            ) 

            # Save the payment intent ID in the order
            order.stripe_payment_intent = intent.id
            order.save()

            # Return the client secret to the frontend so the user can complete the payment
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent': intent.id
            })
        
        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            return Response({
                'error': str(e)
            }, status=400)


# b2c/payments/views.py
@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events (e.g., payment success/failure).
    This view is called when Stripe sends a notification of a successful or failed payment.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', None)  # Use .get() to avoid KeyError
    if not sig_header:
        # Log the headers to investigate why the signature is missing
        print("No Stripe signature header found.")
        return HttpResponse(status=400)

    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        print("Invalid payload received.")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        print("Signature verification failed.")
        return HttpResponse(status=400)

    # Handle different events from Stripe (Payment success or failure)
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent['metadata']['order_id']
        # Handle the successful payment logic (e.g., update order status)
        print(f"Payment for Order {order_id} was successful.")
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        order_id = intent['metadata']['order_id']
        # Handle the failed payment logic
        print(f"Payment for Order {order_id} failed.")

    return HttpResponse(status=200)

