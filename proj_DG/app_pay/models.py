from django.db import models
from django.conf import settings

class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("captured", "Captured"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("pending", "Pending"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="payments"
    )
    quote_id = models.CharField(max_length=255, null=True, blank=True)            # your quote reference (from session or form)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paise = models.BigIntegerField(null=True, blank=True)                  # amount in paise (integer)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # amount in INR for convenience
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    metadata = models.JSONField(null=True, blank=True)                            # store raw payload/extra info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["razorpay_order_id"]),
            models.Index(fields=["razorpay_payment_id"]),
            models.Index(fields=["quote_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"PaymentRecord({self.id}) {self.razorpay_payment_id or self.razorpay_order_id or self.quote_id}"
