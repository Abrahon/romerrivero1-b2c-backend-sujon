import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from b2c.orders.models import Order

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def send_payment_success_notification(sender, instance, **kwargs):
    if instance.payment_status == "success":
        channel_layer = get_channel_layer()
        user = instance.user

        # Build notification message
        message = (
            f"Payment successful for Order ID {instance.id}. "
            f"Amount: {instance.final_amount}. "
            f"User: {user.email}" 
        )

        # Use email or user.id to create a unique group name
        group_name = f"notifications_{user.email.replace('@', '_').replace('.', '_')}"

        # Log for debugging
        logger.info(f"Payment successful for user {user.email}, Order ID {instance.id}")

        # Send notification via Channels
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': message,
            }
        )
