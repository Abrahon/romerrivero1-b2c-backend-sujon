
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



# class StripePaymentIntentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Just a safe response so GET works (mainly for testing/debugging)
#         return Response({
#             "message": "Use POST with order_id to create a payment intent."
#         })

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get('order_id')

#         # Validate order
#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=404)

#         amount_cents = int(order.total_amount * 100)
#         if amount_cents < 10:
#             return Response(
#                 {"error": "Amount too low. Minimum $0.10 required."},
#                 status=400
#             )

#         try:
#             # Create PaymentIntent in Stripe
#             intent = stripe.PaymentIntent.create(
#                 amount=amount_cents,
#                 currency='usd',
#                 metadata={'order_id': order.id},
#             )

#             # Save PaymentIntent ID in the order
#             order.stripe_payment_intent = intent.id
#             order.save(update_fields=['stripe_payment_intent'])

#             return Response({
#                 "client_secret": intent.client_secret,
#                 "payment_intent": intent.id
#             })

#         except stripe.error.StripeError as e:
#             return Response({"error": str(e)}, status=400)




# # @csrf_exempt
# # def stripe_webhook(request):
# #     """
# #     Handle Stripe webhook events securely.
# #     """
# #     payload = request.body
# #     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
# #     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

# #     if not sig_header:
# #         logger.error("Stripe signature header missing.")
# #         return HttpResponse(status=400)

# #     try:
# #         # ✅ Verify event authenticity
# #         event = stripe.Webhook.construct_event(
# #             payload, sig_header, endpoint_secret
# #         )
# #     except ValueError:
# #         logger.error("Invalid payload received.")
# #         return HttpResponse(status=400)
# #     except stripe.error.SignatureVerificationError:
# #         logger.error("Invalid signature received.")
# #         return HttpResponse(status=400)

# #     # 🔹 Process the event
# #     event_type = event.get("type")
# #     intent = event.get("data", {}).get("object", {})
# #     order_id = intent.get("metadata", {}).get("order_id")

# #     if order_id:
# #         try:
# #             order = Order.objects.get(id=order_id)
# #         except Order.DoesNotExist:
# #             logger.error(f"Order {order_id} not found for webhook event {event_type}.")
# #             return HttpResponse(status=404)

# #         if event_type == "payment_intent.succeeded":
# #             order.is_paid = True
# #             order.payment_status = "success"
# #             order.save(update_fields=["is_paid", "payment_status"])
# #             logger.info(f"✅ Payment successful for Order {order_id}.")

# #         elif event_type == "payment_intent.payment_failed":
# #             order.is_paid = False
# #             order.payment_status = "failed"
# #             order.save(update_fields=["is_paid", "payment_status"])
# #             logger.warning(f"❌ Payment failed for Order {order_id}.")

# #     return HttpResponse(status=200)



# # logger = logging.getLogger(__name__)

# @csrf_exempt
# def stripe_webhook(request):
#     """
#     Handle Stripe webhook events for payments.
#     """
#     payload = request.body
#     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

#     # --- Parse event ---
#     if settings.DEBUG:
#         try:
#             event = json.loads(payload)
#         except ValueError:
#             logger.error("Invalid JSON payload in dev.")
#             return HttpResponse(status=400)
#     else:
#         if not sig_header:
#             logger.error("Stripe signature header missing.")
#             return HttpResponse(status=400)

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, endpoint_secret
#             )
#         except ValueError:
#             logger.error("Invalid payload.")
#             return HttpResponse(status=400)
#         except stripe.error.SignatureVerificationError:
#             logger.error("Invalid signature.")
#             return HttpResponse(status=400)

#     # --- Handle event ---
#     event_type = event.get('type')
#     intent = event.get('data', {}).get('object', {})
#     order_id = intent.get('metadata', {}).get('order_id')

#     if order_id:
#         try:
#             order = Order.objects.get(id=order_id)
#         except Order.DoesNotExist:
#             logger.error(f"Order {order_id} not found for webhook event {event_type}.")
#             return HttpResponse(status=404)

#         if event_type == "payment_intent.succeeded":
#             order.is_paid = True
#             order.payment_status = "success"
#             order.save(update_fields=['is_paid', 'payment_status'])
#             logger.info(f"Payment successful for Order {order_id}.")

#         elif event_type == "payment_intent.payment_failed":
#             order.is_paid = False
#             order.payment_status = "failed"
#             order.save(update_fields=['is_paid', 'payment_status'])
#             logger.info(f"Payment failed for Order {order_id}.")

#     return HttpResponse(status=200)

# b2c/orders/views/payment.py

import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from b2c.orders.models import Order
from notifications.models import Notification

# Set Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    """
    Create a Stripe Checkout Session for a given order.
    """
    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Stripe amount is in cents
        amount_cents = int(order.total_amount * 100)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Order {order.order_number}"},
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"https://yourfrontend.com/success?order_number={order.order_number}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"https://yourfrontend.com/cancel?order_number={order.order_number}",
            )

            # Save Stripe session id
            order.stripe_checkout_session_id = session.id
            order.save(update_fields=["stripe_checkout_session_id"])

            return Response({"id": session.id, "url": session.url})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhookView(APIView):
    """
    Handle Stripe webhook events for order payments.
    """
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        except Exception:
            return HttpResponse(status=400)

        # Handle checkout session completed
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")

            try:
                order = Order.objects.get(stripe_checkout_session_id=session_id)
                order.is_paid = True
                order.payment_status = "paid"
                order.save(update_fields=["is_paid", "payment_status"])

                # Notify customer
                Notification.objects.create(
                    user=order.user,
                    title="Payment Successful",
                    message=f"Payment for your order {order.order_number} was successful."
                )
            except Order.DoesNotExist:
                pass 

        # Handle payment failed
        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            # Optional: notify customer of failed payment

        return HttpResponse(status=200)
