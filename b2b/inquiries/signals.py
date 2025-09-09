from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Inquiry
from b2b.order.models import Order, OrderItem

@receiver(post_save, sender=Inquiry)
def create_order_from_inquiry(sender, instance, created, **kwargs):
    if created and instance.is_resolved:
        with transaction.atomic():
            order = Order.objects.create(
                user=instance.user,
                order_status="PENDING",
                inquiry=instance
            )
            OrderItem.objects.create(
                order=order,
                product=instance.product,
                quantity=instance.quantity,
                price_at_time=instance.price_at_inquiry,
            )
