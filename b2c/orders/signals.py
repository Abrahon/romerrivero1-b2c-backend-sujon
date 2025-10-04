from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderTracking

@receiver(post_save, sender=Order)
def handle_new_order(sender, instance, created, **kwargs):
    if created:
        # Always create tracking
        OrderTracking.objects.create(
            order=instance,
            status="PENDING",
            note="Order automatically created"
        )

    # Only send email when final_amount > 0
    if instance.final_amount > 0 and not instance.is_paid:
        send_mail(
            subject=f"Order Confirmation - {instance.order_number}",
            message=(
                f"Hello {instance.user.email},\n\n"
                f"Your order {instance.order_number} has been confirmed.\n"
                f"Total Amount: {instance.final_amount}\n\n"
                "Thank you for shopping with us!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=False,
        )


