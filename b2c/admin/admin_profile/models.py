from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .enums import IndustryTypeChoices


# ---------------------- Admin Profile ---------------------- #
class AdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(default="", blank=True)
    image = models.ImageField(upload_to="admin_profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user} Admin Profile"


# ---------------------- Company Details ---------------------- #
class CompanyDetails(models.Model):
    company_name = models.CharField(max_length=255)
    industry_type = models.CharField(max_length=255, choices=IndustryTypeChoices.choices)
    company_email = models.EmailField(unique=True)
    company_phone = models.CharField(max_length=20, unique=True)
    company_address = models.TextField()
    image = models.ImageField(upload_to="company/", blank=True, null=True)

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # ✅ Allow only one company profile
        if not self.pk and CompanyDetails.objects.exists():
            raise ValidationError("Only one CompanyDetails instance is allowed.")
        return super().save(*args, **kwargs)


# ---------------------- Notifications ---------------------- #


# ---------------------- Email Security ---------------------- #
class EmailSecurity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_security"
    )
    backup_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.email
