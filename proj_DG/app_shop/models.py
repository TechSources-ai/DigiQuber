from django.db import models
from app_login.models import CustomUser
from app_user.models import Profile

class APIToken(models.Model):
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token created at {self.created_at}"

# class Customer(models.Model):
#     customerName = models.ForeignKey(Profile, related_name='customer_customerName', on_delete=models.CASCADE)
#     isActive = models.BooleanField(default=True)
#     def __str__(self):
#         return self.customerName.name

class Balance(models.Model):
    custRefNo = models.CharField(max_length=100, null=True)
    customerName = models.CharField(max_length=100, null=True)
    kyc_status = models.CharField(max_length=10, null=True)
    currency_pair = models.CharField(max_length=20)
    bal_quantity = models.DecimalField(max_digits=20, decimal_places=4)
    blocked_quantity = models.DecimalField(max_digits=20, decimal_places=4)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.currency_pair} - {self.bal_quantity} ({self.blocked_quantity} blocked)"

