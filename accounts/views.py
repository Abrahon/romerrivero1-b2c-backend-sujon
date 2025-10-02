from django.shortcuts import render
from urllib.parse import urlencode
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
from rest_framework.parsers import MultiPartParser, FormParser
User = get_user_model()  

from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import make_random_password

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer, ChangePasswordSerializer
)



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
    # parser_classes = (MultiPartParser, FormParser)

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
    parser_classes = (MultiPartParser, FormParser)

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
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # OTP verified → keep email in session for password reset
        request.session['verified_email'] = serializer.validated_data["user"].email

        return Response({"message": "OTP verified successfully."})




class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

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


# class GoogleLoginView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request):
#         base_url = "https://accounts.google.com/o/oauth2/v2/auth"
#         params = {
#             "client_id": settings.GOOGLE_CLIENT_ID,
#             "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#             "response_type": "code",
#             "scope": "openid email profile",
#             "access_type": "offline", 
#             "prompt": "consent",      
#         }
#         google_auth_url = f"{base_url}?{urlencode(params)}"
#         return Response({"auth_url": google_auth_url})


#  # google login
# class GoogleCallbackView(APIView):
#     def get(self, request):
#         code = request.GET.get("code")
#         if not code:
#             return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=NoCode")

#         # Exchange code for access token
#         token_url = "https://oauth2.googleapis.com/token"
#         data = {
#             "code": code,
#             "client_id": settings.GOOGLE_CLIENT_ID,
#             "client_secret": settings.GOOGLE_CLIENT_SECRET,
#             "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#             "grant_type": "authorization_code",
#         }
#         token_response = requests.post(token_url, data=data).json()
#         access_token = token_response.get("access_token")

#         if not access_token:
#             return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=InvalidToken")

#         # Fetch user info
#         user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
#         user_info = requests.get(user_info_url, params={"access_token": access_token}).json()

#         email = user_info.get("email")
#         name = user_info.get("name", "")

#         if not email:
#             return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=EmailNotFound")

#         # Create or get user
#         user, _ = User.objects.get_or_create(
#             email=email,
#             defaults={"username": email.split("@")[0], "first_name": name},
#         )

#         # Generate JWT
#         refresh = RefreshToken.for_user(user)
#         jwt_token = str(refresh.access_token)

#         # Redirect back to frontend with JWT
#         return redirect(f"{settings.FRONTEND_REDIRECT_URL}?token={jwt_token}")
    
# class GoogleExchangeView(APIView):
#     def post(self, request):
#         code = request.data.get("code")
#         if not code:
#             return Response({"error": "Code is required"}, status=400)

#         token_url = "https://oauth2.googleapis.com/token"
#         data = {
#             "code": code,
#             "client_id": settings.GOOGLE_CLIENT_ID,
#             "client_secret": settings.GOOGLE_CLIENT_SECRET,
#             "redirect_uri": "http://localhost:3000/google/callback",  # must match frontend
#             "grant_type": "authorization_code",
#         }

#         r = requests.post(token_url, data=data)
#         if r.status_code != 200:
#             return Response({"error": r.json()}, status=400)

#         token_data = r.json()
#         access_token = token_data.get("access_token")

#         # Fetch user info
#         user_info = requests.get(
#             "https://www.googleapis.com/oauth2/v3/userinfo",
#             headers={"Authorization": f"Bearer {access_token}"}
#         ).json()

        
#         return Response({"user": user_info})


import requests
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Step 1: Redirect user to Google Auth URL
        """
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",  # to get refresh token
            "prompt": "consent",       # force account selection
        }
        google_auth_url = f"{base_url}?{urlencode(params)}"
        return Response({"auth_url": google_auth_url})


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Step 2: Google redirects here with ?code=...
        We exchange code for token, fetch user info, create user, return JWT
        """
        code = request.GET.get("code")
        if not code:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=NoCode")

        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=data).json()
        access_token = token_response.get("access_token")

        if not access_token:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=InvalidToken")

        # Fetch user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info = requests.get(user_info_url, params={"access_token": access_token}).json()

        email = user_info.get("email")
        name = user_info.get("name", "")

        if not email:
            return redirect(f"{settings.FRONTEND_REDIRECT_URL}?error=EmailNotFound")

        # Create or get user
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "first_name": name},
        )

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)

        # Redirect back to frontend with JWT
        return redirect(f"{settings.FRONTEND_REDIRECT_URL}?token={jwt_token}")


# class GoogleExchangeView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         """
#         Step 3 (alternative flow):
#         Exchange authorization code for user info via POST from frontend
#         """
#         code = request.data.get("code")
#         if not code:
#             return Response({"error": "Code is required"}, status=400)

#         token_url = "https://oauth2.googleapis.com/token"
#         data = {
#             "code": code,
#             "client_id": settings.GOOGLE_CLIENT_ID,
#             "client_secret": settings.GOOGLE_CLIENT_SECRET,
#             "redirect_uri": settings.GOOGLE_REDIRECT_URI,  # must match exactly
#             "grant_type": "authorization_code",
#         }
     
#         r = requests.post(token_url, data=data)
#         if r.status_code != 200:
#             return Response({"error": r.json()}, status=400)

#         token_data = r.json()
#         access_token = token_data.get("access_token")

#         if not access_token:
#             return Response({"error": "Invalid access token"}, status=400)

#         # Fetch user info
#         user_info = requests.get(
#             "https://www.googleapis.com/oauth2/v3/userinfo",
#             headers={"Authorization": f"Bearer {access_token}"}
#         ).json()

#         email = user_info.get("email")
#         name = user_info.get("name", "")

#         if not email:
#             return Response({"error": "No email from Google"}, status=400)

#         # Create or get user
#         user, _ = User.objects.get_or_create(
#             email=email,
#             defaults={"username": email.split("@")[0], "first_name": name},
#         )

#         # Generate JWT
#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "user": {
#                 "id": user.id,
#                 "email": user.email,
#                 "name": user.first_name,
#             },
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#         })
class GoogleExchangeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Code is required"}, status=400)

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
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

        # Only use fields that exist in your custom User model
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"name": name}
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
