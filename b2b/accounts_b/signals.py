from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import B2BUser
from b2b.profiles.models import AdminProfile  # only import what exists

@receiver(post_save, sender=B2BUser)
def create_b2b_admin_profile(sender, instance, created, **kwargs):
    if created and instance.role == "admin":
        AdminProfile.objects.create(user=instance)
