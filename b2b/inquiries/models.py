
from django.db import models
from django.conf import settings
from b2b.product.models import Product
from common .models import TimeStampedModel
from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL 


class Inquiry(TimeStampedModel):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    price_at_inquiry = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Field to store the price at the time of inquiry
    is_resolved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set the price at the time of inquiry (price * quantity)
        self.price_at_inquiry = self.product.price * self.quantity
        super(Inquiry, self).save(*args, **kwargs)

    def __str__(self):
        return f"Inquiry from {self.user.username} - {self.subject}"

    class Meta:
        ordering = ['-created_at']




class AdminNotification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inquiries_admin_notifications',  # unique
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"



