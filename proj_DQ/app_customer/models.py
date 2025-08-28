# app_customer/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, blank=True)
    aadhar_number = models.CharField(max_length=100, blank=True)
    pan_number = models.CharField(max_length=100, blank=True)
    # age = models.PositiveIntegerField(null=True, blank=True)
    # employee_id = models.CharField(max_length=20, blank=True)
    # company = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email if self.user.email else self.user.username

class SessionInfo(models.Model):
    name = models.CharField(max_length=255)
    session_key = models.CharField(max_length=255, blank=True, null=True)
    session_created_at = models.DateTimeField(auto_now_add=True)
    session_expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name