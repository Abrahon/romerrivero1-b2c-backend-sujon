
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from b2c.checkout.models import Shipping
from b2c.orders.models import Order

@receiver(post_save, sender=Shipping)
def send_payment_success_notification(sender, instance, created, **kwargs):
    if created:
        order = instance.order  # Get the associated order from the shipping instance
        
        if order and order.order_status == 'SUCCESS':  # Ensure order status is 'SUCCESS'
            # Send real-time notification for payment success
            channel_layer = get_channel_layer()
            message = f"Payment successful for Order ID {order.id}. Amount: {order.total_amount}"
            group_name = f'notifications_{order.user.username}'  # Notify the user
            channel_layer.group_send(
                group_name,
                {
                    'type': 'send_notification',
                    'message': message
                }
            )
