from django.db import models
from common.models import TimeStampedModel

class Promotion(TimeStampedModel):
    """
    Admin can add promotions/advertisements
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='promotions/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def clean(self):
        # Ensure start_date is before end_date
        if self.end_date < self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("End date must be after start date.")
