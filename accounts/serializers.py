from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

from rest_framework import serializers
from .models import OTP, User
from rest_framework import serializers
from .utils import generate_otp, send_otp_email

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'confirm_password', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        attrs['user'] = user
        return attrs
    


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        code = generate_otp()
        OTP.objects.create(user=user, code=code)

        # ✅ Send OTP using the user's actual name dynamically
        send_otp_email(user.email, code, name=user.name)

        return user

    def to_representation(self, instance):
        
        return {"message": "OTP sent successfully."}

 

class VerifyOTPSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)  

    def validate(self, data):
        request = self.context.get("request")
        email = request.session.get("otp_user_email")  # get email from session

        if not email:
            raise serializers.ValidationError("No OTP request found. Please request OTP first.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        otp = OTP.objects.filter(user=user, code=data["code"]).order_by("-created_at").first()
        if not otp or otp.is_expired():
            raise serializers.ValidationError("OTP is invalid or expired.")

        data["user"] = user
        return data




class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("OTP verification required.")
        self.user = user
        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        OTP.objects.filter(user=self.user).delete()
        return self.user




class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError("Old password is incorrect.")
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
   