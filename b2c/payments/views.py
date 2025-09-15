
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from b2c.orders.models import Order
import stripe
# b2c/payments/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging
import json
import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
  # adjust according to your project

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY



class StripePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Just a safe response so GET works (mainly for testing/debugging)
        return Response({
            "message": "Use POST with order_id to create a payment intent."
        })

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')

        # Validate order
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        amount_cents = int(order.total_amount * 100)
        if amount_cents < 10:
            return Response(
                {"error": "Amount too low. Minimum $0.10 required."},
                status=400
            )

        try:
            # Create PaymentIntent in Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={'order_id': order.id},
            )

            # Save PaymentIntent ID in the order
            order.stripe_payment_intent = intent.id
            order.save(update_fields=['stripe_payment_intent'])

            return Response({
                "client_secret": intent.client_secret,
                "payment_intent": intent.id
            })

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)




# @csrf_exempt
# def stripe_webhook(request):
#     """
#     Handle Stripe webhook events securely.
#     """
#     payload = request.body
#     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

#     if not sig_header:
#         logger.error("Stripe signature header missing.")
#         return HttpResponse(status=400)

#     try:
#         # ✅ Verify event authenticity
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError:
#         logger.error("Invalid payload received.")
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError:
#         logger.error("Invalid signature received.")
#         return HttpResponse(status=400)

#     # 🔹 Process the event
#     event_type = event.get("type")
#     intent = event.get("data", {}).get("object", {})
#     order_id = intent.get("metadata", {}).get("order_id")

#     if order_id:
#         try:
#             order = Order.objects.get(id=order_id)
#         except Order.DoesNotExist:
#             logger.error(f"Order {order_id} not found for webhook event {event_type}.")
#             return HttpResponse(status=404)

#         if event_type == "payment_intent.succeeded":
#             order.is_paid = True
#             order.payment_status = "success"
#             order.save(update_fields=["is_paid", "payment_status"])
#             logger.info(f"✅ Payment successful for Order {order_id}.")

#         elif event_type == "payment_intent.payment_failed":
#             order.is_paid = False
#             order.payment_status = "failed"
#             order.save(update_fields=["is_paid", "payment_status"])
#             logger.warning(f"❌ Payment failed for Order {order_id}.")

#     return HttpResponse(status=200)



# logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events for payments.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # --- Parse event ---
    if settings.DEBUG:
        try:
            event = json.loads(payload)
        except ValueError:
            logger.error("Invalid JSON payload in dev.")
            return HttpResponse(status=400)
    else:
        if not sig_header:
            logger.error("Stripe signature header missing.")
            return HttpResponse(status=400)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload.")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature.")
            return HttpResponse(status=400)

    # --- Handle event ---
    event_type = event.get('type')
    intent = event.get('data', {}).get('object', {})
    order_id = intent.get('metadata', {}).get('order_id')

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found for webhook event {event_type}.")
            return HttpResponse(status=404)

        if event_type == "payment_intent.succeeded":
            order.is_paid = True
            order.payment_status = "success"
            order.save(update_fields=['is_paid', 'payment_status'])
            logger.info(f"Payment successful for Order {order_id}.")

        elif event_type == "payment_intent.payment_failed":
            order.is_paid = False
            order.payment_status = "failed"
            order.save(update_fields=['is_paid', 'payment_status'])
            logger.info(f"Payment failed for Order {order_id}.")

    return HttpResponse(status=200)
