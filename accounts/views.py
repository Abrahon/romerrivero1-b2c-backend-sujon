from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer
from .models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

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

# accounts/views.py



class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]


# class VerifyOTPView(generics.GenericAPIView):
#     serializer_class = VerifyOTPSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response({"message": "OTP is valid."})

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Store verified email in session
        request.session['verified_email'] = serializer.validated_data['email']

        return Response({"message": "OTP verified successfully."})



class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        verified_email = request.session.get("verified_email")

        if not verified_email:
            return Response({"detail": "OTP verification required."}, status=400)

        user = User.objects.filter(email=verified_email).first()

        if not user:
            return Response({"detail": "User not found."}, status=400)

        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clean up the session
        del request.session['verified_email']

        return Response({"message": "Password reset successfully."})




class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
