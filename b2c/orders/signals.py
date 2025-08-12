# order/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        # Send order confirmation email when the order is created
        send_mail(
            subject=f"Order Confirmation - {instance.id}",
            message=f"Your order {instance.id} has been confirmed. Total: {instance.total_price}",
            from_email="no-reply@yourdomain.com",
            recipient_list=[instance.user.email],
        )
