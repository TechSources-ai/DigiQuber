from django.contrib import admin
from .models import PaymentRecord

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quote_id", "razorpay_order_id", "razorpay_payment_id", "status", "amount", "created_at")
    search_fields = ("quote_id", "razorpay_order_id", "razorpay_payment_id", "user__email")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "updated_at")
