from django.db import models
from app_login.models import CustomUser

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    billing_address = models.TextField()
    delivery_address = models.TextField()
    same_as_delivery = models.BooleanField(default=False)  # True if billing address is same as delivery

    def __str__(self):
        return self.name

# Create your models here.
