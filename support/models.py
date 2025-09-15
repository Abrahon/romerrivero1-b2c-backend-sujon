
from django.db import models
from django.utils import timezone

class SupportRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now) 


    def __str__(self):
        return f"Support request from {self.name} ({self.status})"
