from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from b2b.accounts_b.models import B2BUser


from .serializers import (
    B2BSignupSerializer,
    B2BLoginSerializer,
    B2BSendOTPSerializer,
    B2BVerifyOTPSerializer,
    B2BResetPasswordSerializer,
    B2BChangePasswordSerializer
)

User = get_user_model()


# ---------------- Signup ----------------
class B2BSignupView(generics.CreateAPIView):
    serializer_class = B2BSignupSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
            }
        }, status=status.HTTP_201_CREATED)


# ---------------- Login ----------------


class B2BLoginView(generics.GenericAPIView):
    serializer_class = B2BLoginSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure only B2B users can log in
        user = serializer.validated_data['user']
        if not isinstance(user, B2BUser):
            return Response({"detail": "This is not a B2B account."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "token": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)


# ---------------- Send OTP ----------------
class B2BSendOTPView(generics.CreateAPIView):
    serializer_class = B2BSendOTPSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        request.session['otp_user_email'] = user.email
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


# ---------------- Verify OTP ----------------
class B2BVerifyOTPView(generics.GenericAPIView):
    serializer_class = B2BVerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.session['verified_email'] = serializer.validated_data["user"].email
        return Response({"message": "OTP verified successfully."})


# ---------------- Reset Password ----------------
class B2BResetPasswordView(generics.GenericAPIView):
    serializer_class = B2BResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        verified_email = request.session.get("verified_email")
        if not verified_email:
            return Response({"detail": "OTP verification required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=verified_email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        request.session.pop("verified_email", None)

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)


# ---------------- Admin Create ----------------
class B2BAdminCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')

        if not email or not password or not name:
            return Response({"detail": "Name, email, and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                name=name,
                role="ADMIN" 
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Admin user created successfully"}, status=status.HTTP_201_CREATED)
