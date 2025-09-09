from django.db.models.signals import post_save
from django.dispatch import receiver
from b2c.user_profile.models import UserProfile
from b2c.admin.admin_profile.models import AdminProfile
from .models import User 

@receiver(post_save, sender=User)
def create_b2c_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "buyer":
            UserProfile.objects.create(user=instance)
        elif instance.role == "admin":
            AdminProfile.objects.create(user=instance)

