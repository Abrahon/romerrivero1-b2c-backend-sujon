# product/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import Product

@receiver(post_save, sender=Product)
def send_discounted_product_notification(sender, instance, created, **kwargs):
    if created and instance.discount > 0:
        # Notify users when a discounted product is added
        channel_layer = get_channel_layer()
        message = f"New discounted product: {instance.title}, {instance.discount}% off!"
        group_name = "notifications_all_users"
        channel_layer.group_send(
            group_name,
            {
                'type': 'send_notification',
                'message': message
            }
        )
