# from decimal import Decimal
# from django.conf import settings
# from django.db import models
# from django.utils import timezone

# User = settings.AUTH_USER_MODEL

# class Listing(models.Model):
#     seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sell_listings")
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)  # rupees
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} — {self.price}"


# class SellOrder(models.Model):
#     STATUS_PENDING = "pending"
#     STATUS_CAPTURED = "captured"
#     STATUS_FAILED = "failed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, "Pending"),
#         (STATUS_CAPTURED, "Captured"),
#         (STATUS_FAILED, "Failed"),
#         (STATUS_CANCELLED, "Cancelled"),
#     ]

#     listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="sell_orders", null=True, blank=True)
#     buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buy_orders", null=True, blank=True)

#     # total amount in rupees (Decimal)
#     amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

#     # optional unit / quantity fields (helpful for partial-sell flows)
#     quantity = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('1.000'))
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

#     # Razorpay-related
#     razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
#     razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
#     razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

#     # provider session id so webhook can call provider execute
#     provider_session_id = models.CharField(max_length=255, blank=True, null=True)

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def mark_captured(self, payment_id: str = None, signature: str = None):
#         self.status = self.STATUS_CAPTURED
#         if payment_id:
#             self.razorpay_payment_id = payment_id
#         if signature:
#             self.razorpay_signature = signature
#         self.save(update_fields=["status", "razorpay_payment_id", "razorpay_signature", "updated_at"])

#     def mark_failed(self):
#         self.status = self.STATUS_FAILED
#         self.save(update_fields=["status", "updated_at"])

#     def __str__(self):
#         return f"SellOrder #{self.pk} - {self.listing.title if self.listing else 'no-listing'} - {self.amount} ({self.status})"

#     class Meta:
#         ordering = ["-created_at"]


# app_sell/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal

User = settings.AUTH_USER_MODEL


class SellQuote(models.Model):
    METAL_CHOICES = (
        ("GOLD", "Gold"),
        ("SILVER", "Silver"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metal = models.CharField(max_length=10, choices=METAL_CHOICES)

    quote_id = models.CharField(max_length=100, unique=True)
    transaction_ref_no = models.CharField(max_length=100,unique=True)

    rate_per_gram = models.DecimalField(max_digits=12, decimal_places=4)

    requested_qty = models.DecimalField(max_digits=12, decimal_places=4)

    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user} | {self.metal} | {self.quote_id}"

class SellTransaction(models.Model):
    STATUS_CHOICES = (
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metal = models.CharField(max_length=10)

    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    quote = models.OneToOneField(
        SellQuote, on_delete=models.PROTECT, related_name="transaction"
    )

    mmtc_txn_ref = models.CharField(max_length=120, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SELL {self.metal} {self.quantity}g | {self.status}"
