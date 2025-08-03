import random
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .enums import RoleChoices

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=RoleChoices.BUYER, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.BUYER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Specify related_name to avoid reverse accessor clash with the default `auth.User`
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',  # Unique related_name for `groups`
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions_set',  # Unique related_name for `user_permissions`
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)