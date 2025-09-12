from django.db import models

# Create your models here.
# accounts/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import date
from common .models import TimeStampedModel
from .enums import Gender

from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name="user_profile")
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Profile information
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.UNSPECIFIED)
    date_of_birth = models.DateField(null=True, blank=True)

    # Contact information
    country = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)   # store in E.164-like or local format
    contact_email = models.EmailField(blank=True)

    # Address
    address = models.TextField(blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=32, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile for {getattr(self.user, 'username', self.user.email)}"
