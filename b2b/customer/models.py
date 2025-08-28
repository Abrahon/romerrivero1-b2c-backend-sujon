# b2b/customers/models.py
from django.db import models
from django.conf import settings
from .enums import CustomerStatus
from common.models import TimeStampedModel
from b2b.order.models import Order

User = settings.AUTH_USER_MODEL

class Customer(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    status = models.CharField(max_length=50, choices=CustomerStatus.choices, default='Active')
    location = models.CharField(max_length=255, blank=True, null=True)  


    def total_orders(self):
        return Order.objects.filter(user=self.user).count()

    def total_spent(self):
        total = Order.objects.filter(user=self.user).aggregate(models.Sum('total_amount'))['total_amount__sum']
        return total if total else 0.00

    def __str__(self):
        return f"{self.user.username} ({self.company_name})"
