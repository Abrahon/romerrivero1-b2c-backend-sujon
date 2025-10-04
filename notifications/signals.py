# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from b2c.orders.models import Order
from b2c.chat.models import Message
# from b2c.coupons.models import CouponUsage
# from b2c.payments.models import Payment

# Generic function to send notification
def send_real_time_notification(user, title, message, notification_type):
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )

        channel_layer = get_channel_layer()
        group_name = f"notifications_{user.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'notification_id': notification.id
            }
        )
    except Exception as e:
        # Log error for debugging
        print(f"Notification Error: {str(e)}")


# ---------------------- Order Notification ----------------------
@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    if created:
        title = f"New Order: {instance.order_number}"
        message = f"Order {instance.order_number} placed by {instance.user.email}, Total: {instance.total_amount}"
        send_real_time_notification(user=instance.user, title=title, message=message, notification_type="ORDER")


# ---------------------- Message / Support Notification ----------------------
@receiver(post_save, sender=Message)
def message_notification(sender, instance, created, **kwargs):
    if created and instance.receiver:
        title = "New Message"
        message = f"Message from {instance.sender.email}: {instance.content[:100]}"
        send_real_time_notification(user=instance.receiver, title=title, message=message, notification_type="MESSAGE")

