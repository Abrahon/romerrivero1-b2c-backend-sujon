from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from b2b.order.models import OrderItem

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    """Update order total whenever an OrderItem is added/changed/deleted."""
    order = instance.order
    order.update_total()
