from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel

from django.conf import settings
User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,  
        blank=True
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.email[:20]}"



class TrainData(TimeStampedModel):
    id = models.AutoField(primary_key=True)  # normal auto ID
    category = models.CharField(max_length=100)
    context = models.CharField(max_length=255)
    question = models.TextField()
    ai_response = models.TextField()
    keywords = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.category} - {self.question[:30]}"


class ChatBotQuery(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.query[:30]}"

