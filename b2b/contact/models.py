from django.db import models
from django.contrib.auth.models import User
from common .models import TimeStampedModel
from django.conf import settings
User = settings.AUTH_USER_MODEL 

class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    

class AdminNotifications(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contact_admin_notifications',  # unique
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


