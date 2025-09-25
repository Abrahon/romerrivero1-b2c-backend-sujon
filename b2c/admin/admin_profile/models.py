
from django.db import models
from django.conf import settings
from .enums import IndustryTypeChoices
from django.contrib.auth import get_user_model
from django.db import models
from cloudinary.models import CloudinaryField

User = get_user_model()


class AdminProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    image = CloudinaryField("admin_profile", blank=True, null=True)  
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class CompanyDetails(models.Model):
  
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_profile",
        null=True,
        blank=True
    )
    company_name = models.CharField(max_length=255)
    industry_type = models.CharField(
        max_length=50,
        choices=IndustryTypeChoices.choices,
        default=IndustryTypeChoices.OTHER
    )
    company_email = models.EmailField(max_length=55)
    company_phone = models.CharField(max_length=20)
    company_address = models.CharField(max_length=100)
    image = CloudinaryField("company_profile", blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"

  

class Notification(models.Model):
    """Admin notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="notifications_profile")
    message = models.TextField()
    notification_type = models.CharField(max_length=50, blank=True)  # Optional
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
    

# email secuirity


class EmailSecurity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="emailsecurity_profile")
    backup_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.email  

