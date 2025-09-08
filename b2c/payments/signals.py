from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync  # ✅ Important
from b2c.checkout.models import Shipping
from b2c.orders.models import Order
# from channels.layers import get_channel_layer   # ✅ Correct



@receiver(post_save, sender=Shipping)
def send_payment_success_notification(sender, instance, created, **kwargs):
    if created:
        order = instance.order  # Get the associated order from the shipping instance
        
        if order and order.order_status == 'SUCCESS':  # Ensure order status is 'SUCCESS'
            # Get the channel layer
            channel_layer = get_channel_layer()

            # Build the notification message
            message = f"Payment successful for Order ID {order.id}. Amount: {order.total_amount}"

            # Group name based on username
            group_name = f'notifications_{order.user.username}'

            # ✅ Use async_to_sync to call group_send
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'message': message,
                }
            )
