from django.contrib import admin

# Register your models here.
from .models import Inquiry,AdminNotification

admin.site.register(Inquiry)
admin.site.register(AdminNotification)