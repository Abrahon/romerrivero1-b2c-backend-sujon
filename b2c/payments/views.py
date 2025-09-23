
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.conf import settings
# from b2c.orders.models import Order
# import stripe
# # b2c/payments/views.py
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# import logging
# import json
# import stripe
# import logging
# from django.conf import settings
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
#   # adjust according to your project

# logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY



# import stripe
# from django.conf import settings
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.views import APIView
# from b2c.orders.models import Order
# from notifications.models import Notification




# # Set Stripe secret key
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class CreateCheckoutSessionView(APIView):
#     """
#     Create a Stripe Checkout Session for a given order.
#     """
#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Stripe amount is in cents
#         amount_cents = int(order.total_amount * 100)

#         try:
#             session = stripe.checkout.Session.create(
#                 payment_method_types=["card"],
#                 line_items=[{
#                     "price_data": {
#                         "currency": "usd",
#                         "product_data": {"name": f"Order {order.order_number}"},
#                         "unit_amount": amount_cents,
#                     },
#                     "quantity": 1,
#                 }],
#                 mode="payment",
#                 success_url=f"http://localhost:3000/cart?order_id={order.order_number}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"http://localhost:3000/cart?order_id={order.order_number}",
#             )

#             # Save Stripe session id
#             order.stripe_checkout_session_id = session.id
#             order.save(update_fields=["stripe_checkout_session_id"])

#             return Response({"id": session.id, "url": session.url})
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except stripe.error.SignatureVerificationError:
#         logger.error("Stripe signature verification failed")
#         return HttpResponse(status=400)
#     except Exception as e:
#         logger.error(f"Stripe webhook error: {str(e)}")
#         return HttpResponse(status=400)

#     # Handle events
#     if event["type"] == "checkout.session.completed":
#         session = event["data"]["object"]
#         session_id = session.get("id")

#         try:
#             order = Order.objects.get(stripe_checkout_session_id=session_id)
#             order.is_paid = True
#             order.payment_status = "paid"
#             order.order_status = "PROCESSING"
#             order.save(update_fields=["is_paid", "payment_status", "order_status"])

#             Notification.objects.create(
#                 user=order.user,
#                 title="Payment Successful",
#                 message=f"Payment for your order {order.order_number} was successful."
#             )
#         except Order.DoesNotExist:
#             logger.warning(f"Order with session_id {session_id} not found.")

#     return HttpResponse(status=200)


# class StripeWebhookView(APIView):
#     """
#     Stripe webhook for payment events.
#     """
#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#             )
#         except stripe.error.SignatureVerificationError:
#             return HttpResponse(status=400)
#         except Exception:
#             return HttpResponse(status=400)

#         # When payment succeeds
#         if event["type"] == "checkout.session.completed":
#             session = event["data"]["object"]
#             session_id = session.get("id")

#             try:
#                 order = Order.objects.get(stripe_checkout_session_id=session_id)
#                 order.is_paid = True
#                 order.payment_status = "paid"
#                 order.order_status = "PROCESSING" 
#                 order.save(update_fields=["is_paid", "payment_status", "order_status"])

#                 # Notify customer
#                 Notification.objects.create(
#                     user=order.user,
#                     title="Payment Successful",
#                     message=f"Payment for your order {order.order_number} was successful."
#                 )
#             except Order.DoesNotExist:
#                 pass  

#         return HttpResponse(status=200)


# b2c/payments/views.py

# b2c/payments/views.py

import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from b2c.orders.models import Order
from notifications.models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

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
                success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"http://localhost:3000/cart?order_id={order_id}",
            )
            order.stripe_checkout_session_id = session.id
            order.save(update_fields=["stripe_checkout_session_id"])
            return Response({"id": session.id, "url": session.url})
        except Exception as e:
            logger.error(f"Stripe Checkout session creation failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name='dispatch')  # exempt CSRF for class-based view
class StripeWebhookView(APIView):
    authentication_classes = []  # <-- disables DRF auth
    permission_classes = []      # <-- disables DRF permissions

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

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")
            try:
                order = Order.objects.get(stripe_checkout_session_id=session_id)
                order.is_paid = True
                order.payment_status = "paid"
                order.order_status = "PROCESSING"
                order.save(update_fields=["is_paid", "payment_status", "order_status"])

                Notification.objects.create(
                    user=order.user,
                    title="Payment Successful",
                    message=f"Payment for your order {order.order_number} was successful."
                )
            except Order.DoesNotExist:
                pass

        return HttpResponse(status=200)