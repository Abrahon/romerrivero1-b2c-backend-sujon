from django.db import models
from django.conf import settings
from b2b.product.models import Product
# from b2b.inquiries.models import Inquiry
from common.models import TimeStampedModel
from decimal import Decimal
from accounts.models import User

# User = settings.AUTH_USER_MODEL


class Order(TimeStampedModel):
    order_number = models.CharField(max_length=255, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders')  # Changed related_name to 'user_orders'
    # inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='inquiry_orders')  # Changed related_name to 'inquiry_orders'
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_status = models.CharField(max_length=50, default="PENDING")  # Pending, Processing, Shipped, Delivered

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{self.user.id}-{self.created_at.strftime('%Y%m%d%H%M%S')}"
        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        # Calculate line total for the item: quantity * price_at_time
        return self.price_at_time * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"
