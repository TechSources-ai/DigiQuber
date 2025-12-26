
# import uuid
# from decimal import Decimal
# from django.utils import timezone
# from datetime import timedelta
# from app_shop.utils import make_post


# def get_sell_quote(*, session_id, customer_ref_no, metal):

#     currency_pair = "XAU/INR" if metal == "GOLD" else "XAG/INR"

#     payload = {
#         "customerRefNo": customer_ref_no,
#         "currencyPair": currency_pair,
#         "transactionRefNo": str(uuid.uuid4()),
#     }

#     response = make_post(
#         endpoint="TRADE_GET_SELL_QUOTE",
#         payload=payload,
#         token=session_id
#     )

#     if response.get("code") != "Success":
#         raise Exception(f"MMTC SELL QUOTE FAILED: {response}")

#     data = response["data"]

#     return {
#         "quote_id": data["quoteId"],
#         "rate_per_gram": Decimal(data["preTaxAmount"]),
#         "expires_at": timezone.now() + timedelta(milliseconds=int(data["quoteValidityTime"])),
#     }


# def execute_sell_order(*, session_id, profile, quote):

#     quantity = quote.requested_qty.quantize(Decimal("0.0001"))
#     pre_tax_amount = (quote.rate_per_gram * quantity).quantize(Decimal("0.01"))

#     payload = {
#         "customerRefNo": profile.customerRefNo,
#         "quoteId": quote.quote_id,
#         "calculationType": "Q",
#         "billingAddressId": profile.billingAddressId,
#         "quantity": str(quantity),
#         "preTaxAmount": str(pre_tax_amount),
#         "tax1Amt": "0.00",
#         "tax2Amt": "0.00",
#         "totalAmount": str(pre_tax_amount),
#         "transactionDate": timezone.now().isoformat(),
#         "transactionOrderID": str(uuid.uuid4()),
#     }

#     response = make_post(
#         endpoint="TRADE_EXECUTE_ORDER",
#         payload=payload,
#         token=session_id
#     )

#     if response.get("code") != "Success":
#         raise Exception(f"MMTC EXECUTE SELL FAILED: {response}")

#     return response, pre_tax_amount


import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from app_shop.utils import make_post


# -------------------------------------------------
# SELL QUOTE
# -------------------------------------------------
def get_sell_quote(*, session_id, customer_ref_no, metal):
    currency_pair = "XAU/INR" if metal == "GOLD" else "XAG/INR"
    transaction_ref_no = str(uuid.uuid4())

    payload = {
        "customerRefNo": customer_ref_no,
        "currencyPair": currency_pair,
        "transactionRefNo": transaction_ref_no,
    }

    response = make_post(
        endpoint="TRADE_GET_SELL_QUOTE",
        payload=payload,
        token=session_id
    )

    if response.get("code") != "Success":
        raise Exception(f"MMTC SELL QUOTE FAILED: {response}")

    data = response["data"]

    return {
        "quote_id": data["quoteId"],
        "transaction_ref_no": transaction_ref_no,
        "rate_per_gram": Decimal(data["preTaxAmount"]),  # 1g rate
        "expires_at": timezone.now()
        + timedelta(milliseconds=int(data["quoteValidityTime"])),
    }


# -------------------------------------------------
# 🔥 SHARED PAYLOAD BUILDER (CRITICAL FIX)
# -------------------------------------------------
def _build_sell_pg_payload(*, profile, quote):
    quantity = quote.requested_qty.quantize(Decimal("0.0001"))
    amount = (quote.rate_per_gram * quantity).quantize(Decimal("0.01"))

    return {
        "customerRefNo": profile.customerRefNo,
        "quoteId": quote.quote_id,
        #"transactionRefNo": quote.transaction_ref_no,
        "calculationType": "Q",
        "quantity": str(quantity),

        # 🔥 MANDATORY AMOUNT FIELDS
        "preTaxAmount": str(amount),
        "transactionOrderID": str(uuid.uuid4()),
        "transactionDate": timezone.now().replace(tzinfo=None).isoformat(),
        "tax1Amt": "0.00",
        "tax2Amt": "0.00",
        "totalAmount": str(amount),

        # 🔥 MANDATORY FOR PG
        "billingAddressId": profile.billingAddressId,
    }


# -------------------------------------------------
# VALIDATE SELL (Partner PG)
# -------------------------------------------------
def validate_sell_quote_pg(*, session_id, profile, quote):
    payload = _build_sell_pg_payload(profile=profile, quote=quote)

    response = make_post(
        endpoint="TRADE_VALIDATE_ENDPOINT_PG",
        payload=payload,
        token=session_id
    )

    if response.get("code") != "Success":
        raise Exception(f"MMTC SELL VALIDATE FAILED: {response}")

    return response


# -------------------------------------------------
# EXECUTE SELL (Partner PG)
# -------------------------------------------------
def execute_sell_order(*, session_id, profile, quote):
    payload = _build_sell_pg_payload(profile=profile, quote=quote)

    payload.update({
        "currencyPair": "XAU/INR" if quote.metal == "GOLD" else "XAG/INR",
        "transactionOrderID": str(uuid.uuid4()),
        "transactionDate": timezone.now().isoformat(),
        "deliveryAddressId": profile.deliveryAddressId,
    })

    response = make_post(
        endpoint="TRADE_EXECUTE_SELL",
        payload=payload,
        token=session_id
    )

    if response.get("code") != "Success":
        raise Exception(f"MMTC EXECUTE SELL FAILED: {response}")

    return response
