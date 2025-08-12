# payment/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
# from .checkout models import Shipping
# from checkout .models import Shipping
from b2c.checkout.models import Shipping


@receiver(post_save, sender=Shipping)
def send_payment_success_notification(sender, instance, created, **kwargs):
    if created and instance.status == 'SUCCESS':
        # Send real-time notification for payment success
        channel_layer = get_channel_layer()
        message = f"Payment successful for Order ID {instance.order.id}. Amount: {instance.amount}"
        group_name = f'notifications_{instance.order.user.username}'  # Notify the user
        channel_layer.group_send(
            group_name,
            {
                'type': 'send_notification',
                'message': message
            }           
        )
