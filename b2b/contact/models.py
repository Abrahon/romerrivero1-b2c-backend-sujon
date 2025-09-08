from django.db import models
from django.contrib.auth.models import User
from common .models import TimeStampedModel
from django.conf import settings

class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    

class AdminNotifications(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="admin_notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - {self.message[:30]}"

