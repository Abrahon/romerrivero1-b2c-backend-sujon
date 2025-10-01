from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,  
        blank=True
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.email[:20]}"



from django.db import models

class ChatBot(models.Model):
    query = models.CharField(max_length=500)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query[:50]}"


class TrainingData(models.Model):
    CATEGORY_CHOICES = [
        ("FAQ", "FAQ"),
        ("Product Information", "Product Information"),
        ("Service Details", "Service Details"),
        ("Company Policies", "Company Policies"),
        ("Pricing Information", "Pricing Information"),
    ]
    CONTEXT_CHOICES = [
        ("B2C Only", "B2C Only"),
        ("B2B Only", "B2B Only"),
        ("Both Platforms", "Both Platforms"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    context = models.CharField(max_length=50, choices=CONTEXT_CHOICES)
    question = models.TextField()
    ai_response = models.TextField()
    keywords = models.JSONField(default=list)
    pinecone_id = models.PositiveIntegerField(unique=True, blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pinecone_id:
            last = TrainingData.objects.order_by('-pinecone_id').first()
            self.pinecone_id = 1 if not last else last.pinecone_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - {self.question[:50]}"
