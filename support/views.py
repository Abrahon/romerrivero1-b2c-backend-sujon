from rest_framework import generics, status
from rest_framework.response import Response
from .models import SupportRequest
from .serializers import SupportRequestSerializer
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings

class SupportRequestCreateView(generics.CreateAPIView):
    queryset = SupportRequest.objects.all()
    serializer_class = SupportRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        support_request = serializer.save()

        # Send email to admin
        try:
            send_mail(
                subject=f"New Support Request from {support_request.name}",
                message=f"""
                You have received a new support request.

                Name: {support_request.name}
                Email: {support_request.email}
                Message: {support_request.message}

                Submitted At: {support_request.submitted_at}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],  
                fail_silently=False,
            )
        except Exception as e:
            # Log or handle email failure
            return Response({
                "error": "Support request created but failed to send email to admin.",
                "details": str(e),
                "support_request": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
