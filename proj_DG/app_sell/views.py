from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from app_shop.models import Balance,Transaction
from app_user.models import Profile
from app_trade.models import Quote
from app_shop.utils import get_token
from .models import SellQuote, SellTransaction
from .services import get_sell_quote, execute_sell_order,  validate_sell_quote_pg
from .models import SellQuote, SellTransaction
from django_ratelimit.decorators import ratelimit


# ----------------------------
# SELL PAGE
# ----------------------------
@login_required
def sell_page_view(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile or not profile.customerRefNo:
        messages.error(request, "Customer profile not ready")
        return redirect("/")

    balances = Balance.objects.filter(custRefNo=profile.customerRefNo)

    return render(request, "app_sell/sell_page.html", {
        "balances": balances
    })


# ----------------------------
# GET SELL QUOTE (VIEW)
# ----------------------------
@login_required
def sell_quote_view(request):
    if request.method != "POST":
        return redirect("sell_page")

    metal = request.POST.get("metal")
    qty_raw = request.POST.get("quantity")

    if metal not in ("GOLD", "SILVER"):
        messages.error(request, "Invalid metal selected")
        return redirect("sell_page")

    try:
        quantity = Decimal(qty_raw)
    except (InvalidOperation, TypeError):
        messages.error(request, "Invalid quantity")
        return redirect("sell_page")

    if quantity <= 0 or quantity.as_tuple().exponent < -4:
        messages.error(request, "Invalid quantity")
        return redirect("sell_page")

    profile = Profile.objects.filter(user=request.user).first()
    if not profile or not profile.customerRefNo:
        messages.error(request, "Customer profile not ready")
        return redirect("sell_page")

    if not profile.billingAddressId or not profile.deliveryAddressId:
        messages.error(request, "Billing / Delivery address missing")
        return redirect("sell_page")

    currency_pair = "XAU/INR" if metal == "GOLD" else "XAG/INR"

    balance = Balance.objects.filter(
        custRefNo=profile.customerRefNo,
        currency_pair=currency_pair
    ).first()

    if not balance or Decimal(balance.bal_quantity) < quantity:
        messages.error(request, "Insufficient balance")
        return redirect("sell_page")

    session_id = get_token()
    if not session_id:
        messages.error(request, "MMTC login failed")
        return redirect("sell_page")

    try:
        quote_resp = get_sell_quote(
            session_id=session_id,
            customer_ref_no=profile.customerRefNo,
            metal=metal
        )
    except Exception as e:
        messages.error(str(e))
        return redirect("sell_page")

    sell_quote = SellQuote.objects.create(
        user=request.user,
        metal=metal,
        quote_id=quote_resp["quote_id"],
        transaction_ref_no=quote_resp["transaction_ref_no"],
        rate_per_gram=quote_resp["rate_per_gram"],
        requested_qty=quantity,
        expires_at=quote_resp["expires_at"],
    )

    est_amount = (sell_quote.rate_per_gram * quantity).quantize(Decimal("0.01"))

    return render(request, "app_sell/confirm_quote.html", {
        "quote": sell_quote,
        "final_amount": est_amount,
        "expires_at": sell_quote.expires_at,
    })

# @ratelimit(key='ip', rate='5/m', method='POST', block=True)
@login_required
def sell_confirm_view(request):
    if request.method != "POST":
        return redirect("sell_page")

    # -------------------------------------------------
    # 1️⃣ Load & validate SellQuote
    # -------------------------------------------------
    quote = get_object_or_404(
        SellQuote,
        quote_id=request.POST.get("quote_id"),
        user=request.user,
        is_used=False
    )

    if quote.is_expired():
        messages.error(request, "Quote expired")
        return redirect("sell_page")

    profile = Profile.objects.filter(user=request.user).first()
    if not profile or not profile.customerRefNo:
        messages.error(request, "Customer profile not ready")
        return redirect("sell_page")

    if not profile.billingAddressId or not profile.deliveryAddressId:
        messages.error(request, "Billing / Delivery address missing")
        return redirect("sell_page")

    # -------------------------------------------------
    # 2️⃣ Fresh MMTC session
    # -------------------------------------------------
    session_id = get_token()
    if not session_id:
        messages.error(request, "MMTC login failed")
        return redirect("sell_page")

    currency_pair = "XAU/INR" if quote.metal == "GOLD" else "XAG/INR"

    try:
        with transaction.atomic():

            # -------------------------------------------------
            # 3️⃣ Lock balance row
            # -------------------------------------------------
            balance = Balance.objects.select_for_update().filter(
                custRefNo=profile.customerRefNo,
                currency_pair=currency_pair
            ).first()

            if not balance or Decimal(balance.bal_quantity) < quote.requested_qty:
                messages.error(request, "Insufficient balance")
                return redirect("sell_page")

            # -------------------------------------------------
            # 4️⃣ VALIDATE SELL (MMTC Partner PG)
            # -------------------------------------------------
            validate_sell_quote_pg(
                session_id=session_id,
                profile=profile,
                quote=quote
            )

            # -------------------------------------------------
            # 5️⃣ EXECUTE SELL (MMTC Partner PG)
            # -------------------------------------------------
            resp = execute_sell_order(
                session_id=session_id,
                profile=profile,
                quote=quote
            )

            if not resp or resp.get("status") != 200:
                raise Exception("MMTC SELL EXECUTE FAILED")

            order = resp["data"]["orderId"]
            txn_id = order["transactionId"]
            total_amount = Decimal(resp["data"]["totalAmount"])

            # -------------------------------------------------
            # 6️⃣ Update vault balance (DEDUCT)
            # -------------------------------------------------
            balance.bal_quantity = balance.bal_quantity - quote.requested_qty
            balance.balance_as_of = timezone.now()
            balance.save(update_fields=["bal_quantity", "balance_as_of"])

            # -------------------------------------------------
            # 7️⃣ Mark quote used
            # -------------------------------------------------
            quote.is_used = True
            quote.save(update_fields=["is_used"])

            # -------------------------------------------------
            # 8️⃣ Save SELL transaction (UNIFIED LEDGER)
            # -------------------------------------------------
            Transaction.objects.get_or_create(
                orderId=txn_id,   # 🔒 prevents duplicates
                defaults={
                    "customerRefNo": profile.customerRefNo,
                    "user": request.user,
                    "transactionType": "SELL",
                    "currencyPair": currency_pair,
                    "quantity": Decimal("-1") * quote.requested_qty,  # 🔴 NEGATIVE
                    "totalAmt": total_amount,
                    "transactionDate": timezone.now(),
                    "status": "EXECUTED",
                }
            )

            # -------------------------------------------------
            # 9️⃣ (Optional) Keep SellTransaction for internal use
            # -------------------------------------------------
            SellTransaction.objects.create(
                user=request.user,
                metal=quote.metal,
                quantity=quote.requested_qty,
                amount=total_amount,
                quote=quote,
                mmtc_txn_ref=txn_id,
                status="SUCCESS"
            )

    except Exception as e:
        messages.error(request, f"Sell failed: {e}")
        return redirect("sell_page")

    messages.success(request, f"Sell successful. ₹{total_amount} credited.")
    return redirect("sell_page")
