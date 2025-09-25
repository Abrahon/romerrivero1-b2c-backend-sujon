# visitors/middleware.py
from django.utils import timezone
from .models import Visitor

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        print("or here  is ip adddress: " ,ip)
    else:
        ip = request.META.get('REMOTE_ADDR')
        print("or here  is ip adddress: " ,ip)
    return ip

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None
        ip = get_client_ip(request)

        # Save or update visitor
        Visitor.objects.update_or_create(
            user=user,
            ip_address=ip,
            defaults={'last_visit': timezone.now()}
        )

        response = self.get_response(request)
        return response
