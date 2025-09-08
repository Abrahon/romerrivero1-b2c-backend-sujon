from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from accounts.models import User  # <-- your B2C user model

@receiver(post_save, sender=User)   # 🔒 only triggers for B2C users
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
