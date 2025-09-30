
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        
        send_mail(
            subject=f"Order Confirmation - {instance.order_number}",
            message=f"Hello {instance.user.email},\n\nYour order {instance.order_number} has been confirmed.\nTotal Amount: {instance.final_amount}\n\nThank you for shopping with us!",
            from_email=settings.DEFAULT_FROM_EMAIL,  
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import Order

# @receiver(post_save, sender=Order)
# def send_order_confirmation_email(sender, instance, created, **kwargs):
#     if created:
#         try:
#             # Prepare email content
#             subject = f"Order Confirmation - {instance.order_number}"
            
#             message = f"""
# Hello {instance.user.first_name or instance.user.email},

# Your order {instance.order_number} has been placed successfully.

# Order Details:
# ------------------------
# Total Amount: {instance.total_amount:.2f}
# Discounted Amount: {instance.discounted_amount:.2f}
# Final Amount: {instance.final_amount:.2f}
# Payment Method: {instance.payment_method}
# Order Status: {instance.order_status}

# Thank you for shopping with us!
# """

#             # Send email to the customer
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.user.email],
#                 fail_silently=False,
#             )

#             # Optionally notify admins
#             from django.contrib.auth import get_user_model
#             User = get_user_model()
#             admins = User.objects.filter(is_staff=True)
#             for admin in admins:
#                 send_mail(
#                     subject=f"New Order Placed - {instance.order_number}",
#                     message=f"Admin,\n\nA new order {instance.order_number} has been placed by {instance.user.email}.\nFinal Amount: {instance.final_amount:.2f}",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[admin.email],
#                     fail_silently=True,  # Admin notifications shouldn't break main flow
#                 )

#         except Exception as e:
#             # Log error (recommended to use logging in production)
#             import logging
#             logger = logging.getLogger(__name__)
#             logger.error(f"Failed to send order confirmation email: {e}")
