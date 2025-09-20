
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
            message=f"Hello {instance.user.email},\n\nYour order {instance.order_number} has been confirmed.\nTotal Amount: {instance.total_amount}\n\nThank you for shopping with us!",
            from_email=settings.DEFAULT_FROM_EMAIL,  
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
