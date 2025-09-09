from django.db import models
from django.conf import settings
from b2b.product.models import Product
from common.models import TimeStampedModel

User = settings.AUTH_USER_MODEL

# -------------------------------
# Inquiry Model
# -------------------------------
class Inquiry(TimeStampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='inquiries'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    price_at_inquiry = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.price_at_inquiry = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inquiry from {self.user.email} - {self.subject}"


# -------------------------------
# Admin Notification Model
# -------------------------------
class AdminNotification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='inquiries_admin_notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.email}: {self.message[:50]}"
