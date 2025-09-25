from django.db import models
from django.conf import settings
from common.models import TimeStampedModel
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField


User = get_user_model()
class HeroPromotion(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="hero_promotion",
        null=True,
        blank=True
    )
    first_title = models.CharField(max_length=100)
    second_title = models.CharField(max_length=100)
    third_title = models.TextField(blank=True, null=True)
    description = models.TextField(max_length=255)
    product_link = models.URLField(max_length=255, blank=True, null=True)
    hero_image = CloudinaryField('image', blank=True, null=True) 

    def __str__(self):
        return f"{self.first_title} - {self.second_title}"
    


class HeroPromotions(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="hero_promotions",
        null=True,  
        blank=True     
    )
    first_title = models.CharField(max_length=100)
    second_title = models.CharField(max_length=100)
    third_title = models.TextField(blank=True, null=True)
    description = models.TextField(max_length=255)
    product_link = models.URLField(max_length=255, blank=True, null=True)

    # ✅ Cloudinary Image Upload
    hero_image = CloudinaryField('image', blank=True, null=True) 

    def __str__(self):
        return f"{self.first_title} - {self.second_title}"
