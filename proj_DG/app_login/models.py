
# from django.db import models
# from django.contrib.auth.models import (
#     AbstractBaseUser,
#     BaseUserManager,
#     PermissionsMixin,
# )
# from django.utils import timezone
# from datetime import timedelta
# import random
# import string


# # =========================
# # Custom User Manager
# # =========================
# class CustomUserManager(BaseUserManager):
#     def create_user(self, email=None, phone=None, password=None, **extra_fields):
#         if not email and not phone:
#             raise ValueError("Email or phone number must be provided")

#         if email:
#             email = self.normalize_email(email)

#         user = self.model(email=email, phone=phone, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")

#         return self.create_user(email=email, password=password, **extra_fields)


# # =========================
# # Custom User Model
# # =========================
# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     """
#     Custom user supporting login via email OR phone.
#     PermissionsMixin provides groups, permissions, is_superuser.
#     """
#     email = models.EmailField(unique=True, null=True, blank=True)
#     phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.email or self.phone or "User"


# def email_token_expiry():
#     return timezone.now() + timedelta(minutes=5)

# class EmailVerification(models.Model):
#     email = models.EmailField(unique=True)
#     token = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     valid_until = models.DateTimeField(default=email_token_expiry)
#     is_used = models.BooleanField(default=False)

#     @staticmethod
#     def generate_token():
#         return "".join(random.choices(string.digits, k=6))

#     def is_valid(self):
#         return (not self.is_used) and timezone.now() < self.valid_until

# # =========================
# # Phone Verification (OTP)
# # =========================
# class PhoneVerification(models.Model):
#     phone = models.CharField(max_length=15, unique=True)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     valid_until = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))
#     is_used = models.BooleanField(default=False)

#     @staticmethod
#     def generate_otp():
#         return "".join(random.choices(string.digits, k=6))

#     def is_valid(self):
#         return (not self.is_used) and timezone.now() < self.valid_until

#     def __str__(self):
#         return self.phone






from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from datetime import timedelta
import random
import string


# =========================
# Custom User Manager
# =========================
class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Email or phone number must be provided")

        if email:
            email = self.normalize_email(email)

        user = self.model(email=email, phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not password:
            raise ValueError("Superuser must have a password")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


# =========================
# Custom User Model
# =========================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user supporting login via email OR phone.
    """
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or self.phone or "User"


# =====================================================
# Email Verification (OTP-based, NO email link anymore)
# =====================================================

def email_otp_expiry():
    return timezone.now() + timedelta(minutes=5)


class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=email_otp_expiry)
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_token():
        return "".join(random.choices(string.digits, k=6))

    def is_valid(self):
        return (not self.is_used) and timezone.now() < self.valid_until

    def __str__(self):
        return self.email


# =========================
# Phone Verification (OTP)
# =========================

def phone_otp_expiry():
    return timezone.now() + timedelta(minutes=5)


class PhoneVerification(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=phone_otp_expiry)
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_otp():
        return "".join(random.choices(string.digits, k=6))

    def is_valid(self):
        return (not self.is_used) and timezone.now() < self.valid_until

    def __str__(self):
        return self.phone

def email_token_expiry():
    return timezone.now() + timedelta(minutes=5)
