from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import ContactMessage, AdminNotifications
from .serializers import ContactMessageSerializer

User = get_user_model()


class ContactMessageCreateAPIView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        message = serializer.save()

        # --- Send Email to Admin ---
        admin_email = getattr(settings, "ADMIN_EMAIL", None)
        default_from = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        if admin_email and default_from:
            try:
                send_mail(
                    subject=f"New Contact Form Message from {message.name}",
                    message=f"Name: {message.name}\nEmail: {message.email}\n\nMessage:\n{message.message}",
                    from_email=default_from,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log error, but don’t crash
                print(f"Email sending failed: {e}")

        # --- Create Notifications for Superusers ---
        try:
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                AdminNotifications.objects.create(
                    user=admin,
                    message=f"New contact message from {message.name}",
                )
        except Exception as e:
            print(f"Notification creation failed: {e}")

        return message

    def create(self, request, *args, **kwargs):
        """Custom create with error handling"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except serializers.ValidationError as ve:
            return Response({"success": False, "error": ve.detail}, status=400)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)

        return Response(
            {"success": True, "message": "Message sent successfully!"},
            status=201,
        )
