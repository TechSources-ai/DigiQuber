# from django.contrib import admin
# from .models import Listing, SellOrder

# @admin.register(Listing)
# class ListingAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "seller", "price", "is_active", "created_at")
#     list_filter = ("is_active", "created_at", "seller")
#     search_fields = ("title", "description", "seller__email")

# @admin.register(SellOrder)
# class SellOrderAdmin(admin.ModelAdmin):
#     list_display = ("id", "listing", "buyer", "amount", "status", "razorpay_order_id", "created_at")
#     list_filter = ("status", "created_at")
#     search_fields = ("buyer__email", "razorpay_order_id", "listing__title")
