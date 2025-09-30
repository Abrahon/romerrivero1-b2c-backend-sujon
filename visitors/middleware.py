# visitors/middleware.py
from django.utils import timezone
from .models import Visitor
from django.db import IntegrityError

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    print("Visitor IP:", ip)
    return ip

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        ip = get_client_ip(request)

        try:
            # Use update_or_create safely
            Visitor.objects.update_or_create(
                user=user,
                ip_address=ip,
                defaults={'last_visit': timezone.now()}
            )
        except IntegrityError:
            # Rare case: race condition caused duplicate, just update the latest
            visitor = Visitor.objects.filter(user=user, ip_address=ip).first()
            if visitor:
                visitor.last_visit = timezone.now()
                visitor.save()

        response = self.get_response(request)
        return response
