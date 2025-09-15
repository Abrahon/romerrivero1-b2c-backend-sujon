from django.db import models

class NotificationType(models.TextChoices):
    ORDER = "ORDER", "New Order"
    MESSAGE = "MESSAGE", "Message / Support"
    COUPON = "COUPON", "Coupon / Discount Usage"
    PAYMENT = "PAYMENT", "Payment"
