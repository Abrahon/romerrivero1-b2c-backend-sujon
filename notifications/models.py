from django.db import models
from .enums import NotificationType
from django.conf import settings
from common.models import TimeStampedModel

class Notification(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.MESSAGE
    )
    is_read = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.notification_type} for {self.user.email}"

