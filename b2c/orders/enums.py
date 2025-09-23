
from django.db import models

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    DELIVERD = 'success', 'Deliverd'
    CANCELL = 'cancelled', 'Cancelled',


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PaymentMethodChoices(models.TextChoices):
    COD = "COD", "Cash on Delivery"
    ONLINE = "ONLINE", "Online Payment"


    
