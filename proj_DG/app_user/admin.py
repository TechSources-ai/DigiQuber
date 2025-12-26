from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "customerRefNo",
        "dgcustomerRefNo",
        "billingAddressId",
        "deliveryAddressId",
        "kycStatus",
    )

    search_fields = (
        "user__email",
        "customerRefNo",
        "dgcustomerRefNo",
        "billingAddressId",
    )

    list_filter = ("kycStatus",)

    readonly_fields = (
        "customerRefNo",
        "dgcustomerRefNo",
        "billingAddressId",
        "deliveryAddressId",
    )
