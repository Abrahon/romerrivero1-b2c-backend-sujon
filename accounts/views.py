from django.shortcuts import render
from urllib.parse import urlencode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, LoginSerializer
from .models import User, OTP
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
)
import requests
from django.conf import settings
from django.shortcuts import redirect
import time
import datetime

User = get_user_model()

# ==================== YOUR ORIGINAL VIEWS (UNCHANGED) ====================
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User created successfully",
            "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
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
            "token": {"refresh": str(refresh), "access": str(refresh.access_token)},
            "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
        }, status=status.HTTP_200_OK)

class SendOTPView(generics.CreateAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        request.session['otp_user_email'] = user.email
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.session['verified_email'] = serializer.validated_data["user"].email
        return Response({"message": "OTP verified successfully."})

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp_code = request.data.get("otp")
        if not email or not otp_code:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        otp = OTP.objects.filter(user=user, code=str(otp_code).strip()).order_by("-created_at").first()
        if not otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        if otp.is_expired():
            return Response({"detail": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
        otp.delete()
        serializer = self.get_serializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

class AdminCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        if not email or not password or not name:
            return Response({"detail": "Name, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_superuser(email=email, password=password, name=name)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Admin user created successfully"}, status=status.HTTP_201_CREATED)

# ==================== FIXED TOKEN VIEWS ====================
class CheckTokenView(APIView):
    """✅ FIXED: 10s token check with countdown"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        remaining = request.auth['exp'] - int(time.time())
        return Response({
            "valid": True,
            "email": request.user.email,
            "remaining_seconds": remaining,
            "message": f"Token expires in {remaining} seconds"
        }, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            refresh_token = request.data.get("refresh")
            validated_refresh = RefreshToken(refresh_token)
            user_id = validated_refresh.payload['user_id']  # ✅ FIXED!
            user = User.objects.get(id=user_id)
            
            return Response({
                "success": True,
                "message": "Token refreshed! New access = 10 seconds",
                "tokens": {
                    "access": response.data['access'],
                    "refresh": str(validated_refresh)
                },
                "user": {
                    "id": user.id, "email": user.email,
                    "name": getattr(user, "name", ""),
                    "role": getattr(user, "role", "")
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Invalid refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)

# ==================== GOOGLE VIEWS (UNCHANGED) ====================
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        google_auth_url = f"{base_url}?{urlencode(params)}"
        return Response({"auth_url": google_auth_url})

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=NoCode")
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code, "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=data).json()
        access_token = token_response.get("access_token")
        if not access_token:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=InvalidToken")
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", params={"access_token": access_token}).json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        if not email:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=EmailNotFound")
        user, _ = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "first_name": name},
        )
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)
        return redirect(f"{settings.FRONTEND_REDIRECT_URL}?token={jwt_token}")

class GoogleExchangeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Code is required"}, status=400)
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": urlencode(code), "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            return Response({"error": r.json()}, status=400)
        token_data = r.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return Response({"error": "Invalid access token"}, status=400)
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        if not email:
            return Response({"error": "No email from Google"}, status=400)
        user, _ = User.objects.get_or_create(email=email, defaults={"name": name})
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "refresh": str(refresh), "access": str(refresh.access_token),
        })

class GoogleSignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Code is required"}, status=400)
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": urlencode(code), "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            return Response({"error": "Failed to get token", "details": token_response.json()}, status=400)
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return Response({"error": "Invalid access token"}, status=400)
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        if not email:
            return Response({"error": "No email returned from Google"}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists. Please login."}, status=400)
        user = User.objects.create(email=email, username=email.split("@")[0], first_name=name)
        refresh = RefreshToken.for_user(user)
        access_token_jwt = str(refresh.access_token)
        return Response({
            "user": {"id": user.id, "email": user.email, "name": user.first_name},
            "refresh": str(refresh), "access": access_token_jwt,
            "message": "Signup successful"
        }, status=201)