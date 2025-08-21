# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification
from b2c.admin.add_product.models import Wishlist,Product
from b2c.chat.models import Message
# from products.models import Product
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()

# When user adds wishlist
@receiver(post_save, sender=Wishlist)
def notify_wishlist(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type="wishlist",
            title="Product added to Wishlist",
            message=f"You added {instance.product.name} to your wishlist."
        )

# When user sends message
@receiver(post_save, sender=Message)
def notify_admin_message(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type="message",
                title="New User Message",
                message=f"{instance.sender.email} sent you a message: {instance.text[:30]}..."
            )

# When admin adds offer product
@receiver(post_save, sender=Product)
def notify_offer(sender, instance, created, **kwargs):
    if created and instance.is_offer:  # assuming you have a field `is_offer=True`
        users = User.objects.filter(is_active=True)
        for user in users:
            Notification.objects.create(
                user=user,
                notification_type="offer",
                title="New Offer!",
                message=f"{instance.name} is now on offer! Grab it fast."
            )



def broadcast_notification(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "data": data
        }
    )
