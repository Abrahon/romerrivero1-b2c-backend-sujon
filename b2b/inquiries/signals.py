# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from b2b.inquiries.models import Inquiry
# from b2b.order.models import Order, OrderItem
# from django.db import transaction

# @receiver(post_save, sender=Inquiry)
# def create_order_from_inquiry(sender, instance, created, **kwargs):
#     if created and instance.is_resolved:  # Only create order when inquiry is resolved
#         with transaction.atomic():  # Ensure atomicity
#             # Create the order
#             order = Order.objects.create(
#                 user=instance.user,
#                 order_status="PENDING",
#                 inquiry=instance
#             )

#             # Create the order item
#             item = OrderItem.objects.create(
#                 order=order,
#                 product=instance.product,
#                 quantity=instance.quantity,
#                 price_at_time=instance.price_at_inquiry,
#             )

#             # **Update total_amount immediately**
#             order.total_amount = sum(i.line_total for i in order.items.all())
#             order.save()

#             # Reduce the product stock
#             instance.product.available_stock -= instance.quantity
#             instance.product.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from b2b.inquiries.models import Inquiry
from b2b.order.models import Order, OrderItem

@receiver(post_save, sender=Inquiry)
def create_order_from_inquiry(sender, instance, created, **kwargs):
    if created and instance.is_resolved:
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=instance.user,
                order_status="PENDING",
                inquiry=instance
            )

            # Create order item
            OrderItem.objects.create(
                order=order,
                product=instance.product,
                quantity=instance.quantity,
                price_at_time=instance.price_at_inquiry,
            )

            # total_amount will automatically update via the post_save signal of OrderItem
