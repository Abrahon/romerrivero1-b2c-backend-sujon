from django.db import models
from .enums import IndustryTypeChoices
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
# from django.contrib.auth import get_user_model
# User = get_user_model()

class UserProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CompanyDetails(models.Model):
    company_name = models.CharField(max_length=255)
    industry_type = models.CharField(
        max_length=50,
        choices=IndustryTypeChoices.choices,
        default=IndustryTypeChoices.OTHER
    )
    company_name = models.EmailField(max_length=55)
    company_phone = models.CharField(max_length=20)
    company_address = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"

