from django.db import models
from accounts.models import User
from common.models import TimeStampedModel

# Create your models here.

class Shipping(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping')
    full_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    email = models.EmailField()
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100)
    floor = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.full_name}-{self.city}"
    



    