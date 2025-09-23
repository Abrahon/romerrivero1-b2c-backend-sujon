# visitors/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Visitor(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_visit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user or self.ip_address} - {self.last_visit}"
