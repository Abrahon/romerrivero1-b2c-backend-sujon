
from django.db import models
from django.utils import timezone
from django.conf import settings
from b2b.inquiries.models import Inquiry
from b2b.product.models import Product
from common.models import TimeStampedModel 

User = settings.AUTH_USER_MODEL

class Order(TimeStampedModel):
    order_number = models.CharField(max_length=255, unique=True, editable=False) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders')  # Correct related_name
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='inquiry_orders', null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_status = models.CharField(max_length=50, default="PENDING") 
    total_orders = models.PositiveIntegerField(default=0)  # Track total orders for the user

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            ts = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD-{self.user.id}-{ts}"

        # Update total_amount and total_orders before saving
        self.update_total()
        super().save(*args, **kwargs)

    def update_total(self):
        """Recalculate total_amount from order items."""
        total = sum(item.line_total for item in self.items.all())
        self.total_amount = total
        self.total_orders = self.user.user_orders.count()  # Update total orders for the user
        self.save(update_fields=['total_amount', 'total_orders'])

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        # The price is based on the price_at_time to capture the price at the time of purchase.
        return self.price_at_time * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

