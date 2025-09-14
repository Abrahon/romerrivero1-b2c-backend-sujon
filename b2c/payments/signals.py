# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync  # ✅ Important
# from b2c.checkout.models import Shipping
# from b2c.orders.models import Order

# @receiver(post_save, sender=Shipping)
# def send_payment_success_notification(sender, instance, created, **kwargs):
#     if created:
#         order = instance.order  
        
#         if order and order.order_status == 'SUCCESS':  
#             channel_layer = get_channel_layer()

#             message = f"Payment successful for Order ID {order.id}. Amount: {order.total_amount}"

#             group_name = f'notifications_{order.user.username}'

    
#             async_to_sync(channel_layer.group_send)(
#                 group_name,
#                 {
#                     'type': 'send_notification',
#                     'message': message,
#                 }
#             )

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from b2c.orders.models import Order

@receiver(post_save, sender=Order)
def send_payment_success_notification(sender, instance, **kwargs):
    if instance.payment_status == "success":
        channel_layer = get_channel_layer()
        message = f"Payment successful for Order ID {instance.id}. Amount: {instance.total_amount}"

        group_name = f"notifications_{instance.user.username}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': message,
            }
        )
