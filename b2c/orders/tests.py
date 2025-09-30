from django.test import TestCase

# Create your tests here.
# b2c/orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        # Fix: Use 'total_amount' instead of 'total_price'
        send_mail(
            subject=f"Order Confirmation - {instance.order_number}",
            message=f"Your order {instance.order_number} has been confirmed. Total: {instance.final_ammount}",
            from_email="no-reply@yourdomain.com",
            recipient_list=[instance.user.email],
        )
