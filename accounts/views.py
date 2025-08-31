from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, LoginSerializer
from .models import User
# from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAdminUser

User = get_user_model()  

from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import make_random_password

from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
)

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
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


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
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



class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Store user's email in session so VerifyOTPView can identify the user without asking for email
        request.session['otp_user_email'] = user.email

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # OTP verified → keep email in session for password reset
        request.session['verified_email'] = serializer.validated_data["user"].email

        return Response({"message": "OTP verified successfully."})




class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Retrieve the email from session
        verified_email = request.session.get("verified_email")

        if not verified_email:
            return Response({"detail": "OTP verification required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user by email stored in session
        user = User.objects.filter(email=verified_email).first()

        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use the user to reset the password
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clean up the session
        if "verified_email" in request.session:
            del request.session["verified_email"]

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)





class AdminCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]  # Only admins can access

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
                name=name
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Admin user created successfully"},
                        status=status.HTTP_201_CREATED) 