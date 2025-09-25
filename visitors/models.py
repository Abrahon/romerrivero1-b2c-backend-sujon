# visitors/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Visitor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')
    last_visit = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'ip_address')
