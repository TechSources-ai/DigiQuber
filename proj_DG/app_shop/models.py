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
    balance_as_of = models.DateTimeField(null=True)
    blocked_quantity = models.DecimalField(max_digits=20, decimal_places=4)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.currency_pair} - {self.bal_quantity} ({self.blocked_quantity} blocked)"


class Holding(models.Model):
    METAL_CHOICES = [
        ("GOLD", "Gold"),
        ("SILVER", "Silver"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="holdings")

    metal_type = models.CharField(max_length=10, choices=METAL_CHOICES)
    weight = models.DecimalField(max_digits=20, decimal_places=4)
    price_per_gram = models.DecimalField(max_digits=20, decimal_places=4)
    total_price = models.DecimalField(max_digits=20, decimal_places=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.weight}g {self.metal_type}"
    

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("BUY", "Buy"),
        ("SELL", "Sell"),
    ]

    customerRefNo = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    transactionType = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )

    currencyPair = models.CharField(max_length=20)   # XAU/INR, XAG/INR

    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    totalAmt = models.DecimalField(max_digits=20, decimal_places=2)

    orderId = models.CharField(max_length=100, unique=True)

    status = models.CharField(
        max_length=20,
        default="EXECUTED"
    )

    transactionDate = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customerRefNo} {self.transactionType} {self.quantity}"
