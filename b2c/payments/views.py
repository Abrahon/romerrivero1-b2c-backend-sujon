

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



# logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class CreateCheckoutSessionView(APIView):
#     permission_classes = [] 

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

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
#                 success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"http://localhost:3000/cart?order_id={order_id}",
#             )
#             order.stripe_checkout_session_id = session.id
#             order.save(update_fields=["stripe_checkout_session_id"])
#             return Response({"id": session.id, "url": session.url})
#         except Exception as e:
#             logger.error(f"Stripe Checkout session creation failed: {e}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# import logging
# import stripe
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from b2c.orders.models import Order

# logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY

# class CreateCheckoutSessionView(APIView):
#     permission_classes = []  

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        
#         amount_cents = int(order.final_amount * 100)
#         print(amount_cents)

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
#                 success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"http://localhost:3000/cart?order_id={order_id}",
#             )
#             order.stripe_checkout_session_id = session.id
#             order.save(update_fields=["stripe_checkout_session_id"])
#             return Response({"id": session.id, "url": session.url})
#         except Exception as e:
#             logger.error(f"Stripe Checkout session creation failed: {e}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# import logging
# import stripe
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from b2c.orders.models import Order

# logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY

# class CreateCheckoutSessionView(APIView):
#     # permission_classes = [IsAuthenticated]  # ✅ Require auth

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

#         if not order.final_amount or order.final_amount <= 0:
#             return Response({"error": "Order amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

#         amount_cents = int(order.final_amount * 100)
#         logger.info(f"Stripe Checkout: creating session for order {order.order_number} with amount {amount_cents}")

#         try:
#             session = stripe.checkout.Session.create(
#                 payment_method_types=["card"],
#                 line_items=[{
#                     "price_data": {
#                         "currency": "usd",  # or "bdt" if your account supports it
#                         "product_data": {"name": f"Order {order.order_number}"},
#                         "unit_amount": amount_cents,
#                     },
#                     "quantity": 1,
#                 }],
#                 mode="payment",
#                 success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"http://localhost:3000/cart?order_id={order_id}",
#             )
#             order.stripe_checkout_session_id = session.id
#             order.save(update_fields=["stripe_checkout_session_id"])

#             return Response({"id": session.id, "url": session.url})
#         except Exception as e:
#             logger.error(f"Stripe Checkout session creation failed: {str(e)}")
#             return Response({"error": "Stripe session creation failed, please try again later."})
                           

# import logging
# import stripe
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated

# from b2c.orders.models import Order

# logger = logging.getLogger(__name__)
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class CreateCheckoutSessionView(APIView):
#     # permission_classes = [IsAuthenticated]  # ✅ Only authenticated users can pay

#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Ensure order belongs to logged-in user
#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

#         # ✅ Ensure order has a valid payable amount
#         if not order.final_amount or order.final_amount <= 0:
#             return Response({"error": "Order amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

#         # Stripe expects amount in cents
#         amount_cents = int(order.final_amount * 100)
#         logger.info(f"Stripe Checkout: Creating session for Order {order.order_number} - {order.final_amount} ({amount_cents} cents)")

#         try:
#             session = stripe.checkout.Session.create(
#                 payment_method_types=["card"],
#                 line_items=[{
#                     "price_data": {
#                         "currency": "usd",  # ⚠️ Or "bdt" if Stripe supports it for your account
#                         "product_data": {
#                             "name": f"Order {order.order_number}"
#                         },
#                         "unit_amount": amount_cents,
#                     },
#                     "quantity": 1,
#                 }],
#                 mode="payment",
#                 success_url=f"http://localhost:3000/cart?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"http://localhost:3000/cart?order_id={order_id}",
#             )

#             # ✅ Store checkout session id for tracking
#             order.stripe_checkout_session_id = session.id
#             order.save(update_fields=["stripe_checkout_session_id"])

#             return Response({
#                 "id": session.id,
#                 "url": session.url,
#                 "final_amount": str(order.final_amount),  # show discounted final amount
#             }, status=200)

#         except Exception as e:
#             logger.error(f"Stripe Checkout session creation failed: {str(e)}")
#             return Response(
#                 {"error": "Stripe session creation failed, please try again later."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# @method_decorator(csrf_exempt, name='dispatch')  # exempt CSRF for class-based view
# class StripeWebhookView(APIView):
#     authentication_classes = []  
#     permission_classes = []     

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

#         if event["type"] == "checkout.session.completed":
#             session = event["data"]["object"]
#             session_id = session.get("id")
#             try:
#                 order = Order.objects.get(stripe_checkout_session_id=session_id)
#                 order.is_paid = True
#                 order.payment_status = "paid"
#                 order.order_status = "PROCESSING"
#                 order.save(update_fields=["is_paid", "payment_status", "order_status"])

#                 Notification.objects.create(
#                     user=order.user,
#                     title="Payment Successful",
#                     message=f"Payment for your order {order.order_number} was successful."
#                 )
#             except Order.DoesNotExist:
#                 pass

#         return HttpResponse(status=200)
import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from b2c.orders.models import Order, Notification

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can pay

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if not order.final_amount or order.final_amount <= 0:
            return Response({"error": "Order amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

        amount_cents = int(order.final_amount * 100)
        print("final ammount",amount_cents )
        logger.info(f"Stripe Checkout: Creating session for Order {order.order_number} - {order.final_amount} ({amount_cents} cents)")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",  # ⚠️ Change to "bdt" if supported
                        "product_data": {
                            "name": f"Order {order.order_number}"
                        },
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

            return Response({
                "id": session.id,
                "url": session.url,
                "final_amount": str(order.final_amount),
            }, status=200)

        except Exception as e:
            logger.error(f"Stripe Checkout session creation failed: {str(e)}")
            return Response({"error": "Stripe session creation failed, please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
# class StripeWebhookView(APIView):
#     authentication_classes = []  # Public webhook
#     permission_classes = []

#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#             )
#         except stripe.error.SignatureVerificationError:
#             logger.warning("Stripe webhook signature verification failed")
#             return HttpResponse(status=400)
#         except Exception as e:
#             logger.error(f"Stripe webhook error: {str(e)}")
#             return HttpResponse(status=400)

#         # Payment succeeded
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
#                 logger.error(f"Stripe session ID {session_id} not linked to any order")

#         return HttpResponse(status=200)
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []  # public webhook
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        except Exception as e:
            return HttpResponse(status=400)

        # Payment succeeded
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")

            try:
                order = Order.objects.get(stripe_checkout_session_id=session_id)
                
                # Avoid double processing
                if not order.is_paid:
                    order.is_paid = True
                    order.payment_status = "paid"
                    order.order_status = "PROCESSING"  # <-- set to processing automatically
                    order.save(update_fields=["is_paid", "payment_status", "order_status"])

                    # Notify customer
                    Notification.objects.create(
                        user=order.user,
                        title="Payment Successful",
                        message=f"Payment for your order {order.order_number} was successful. Your order is now processing."
                    )

            except Order.DoesNotExist:
                logger.error(f"Stripe session ID {session_id} not linked to any order")

        return HttpResponse(status=200)
