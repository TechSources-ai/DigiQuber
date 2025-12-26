# # app_pay/views.py
# import json
# import hmac
# import hashlib
# import logging
# from decimal import Decimal, InvalidOperation

# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseServerError
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from django.utils import timezone
# from app_shop.utils import make_post

# import razorpay

# from .models import PaymentRecord

# logger = logging.getLogger(__name__)

# # Attempt to import Balance model (adjusted path)
# from app_shop.models import Balance

# # Optional imports for fallback lookup of quantity/customer (if Quote model exists)
# try:
#     from app_trade.models import Quote
# except Exception:
#     Quote = None

# # Optional Profile import for custRefNo fallback
# try:
#     from app_user.models import Profile
# except Exception:
#     Profile = None


# def get_razorpay_client():
#     """
#     Lazy init for razorpay client. Returns None if not configured/failed.
#     """
#     try:
#         key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
#         key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)
#         if not key_id or not key_secret:
#             logger.error("Razorpay keys not configured in settings.")
#             return None
#         return razorpay.Client(auth=(key_id, key_secret))
#     except Exception as e:
#         logger.exception("Failed to init razorpay client: %s", e)
#         return None


# def _create_balance_from_payment(payment_record):
#     """
#     Creates/updates user Balance after a successful BUY payment.
#     This version includes:
#       ✔ correct quantity extraction
#       ✔ correct currencyPair handling
#       ✔ supports metadata injected from payment_success
#       ✔ prevents zero/None qty issues
#       ✔ increments existing balance instead of overwriting
#     """
#     try:
#         if not payment_record:
#             return False

#         meta = payment_record.metadata or {}

#         # prevent duplicate processing
#         if meta.get("balance_created"):
#             logger.debug("Balance already created for PaymentRecord id=%s", getattr(payment_record, "id", None))
#             return False

#         # ----------------------------------------------------
#         # 1) DETERMINE QUANTITY
#         # ----------------------------------------------------
#         qty = None

#         # priority: metadata added during payment_success
#         if meta.get("quantity") is not None:
#             try:
#                 qty = Decimal(str(meta.get("quantity")))
#             except Exception:
#                 qty = None

#         # fallback: other metadata keys
#         if qty is None:
#             for k in ("purchased_quantity", "qty", "session_qty"):
#                 if meta.get(k) is not None:
#                     try:
#                         qty = Decimal(str(meta.get(k)))
#                         break
#                     except Exception:
#                         qty = None

#         # fallback: Quote table lookup
#         quote_obj = None
#         if qty is None and getattr(payment_record, "quote_id", None) and Quote is not None:
#             try:
#                 quote_obj = Quote.objects.filter(quoteId=payment_record.quote_id).first()
#                 if quote_obj and getattr(quote_obj, "quantity", None) is not None:
#                     try:
#                         qty = Decimal(str(quote_obj.quantity))
#                     except Exception:
#                         qty = None
#             except Exception:
#                 logger.exception("Error fetching Quote for qty lookup")

#         # reject missing qty
#         if qty is None or qty == Decimal("0"):
#             logger.info("Skipping balance creation: missing or zero qty for PaymentRecord id=%s", getattr(payment_record, "id", None))
#             return False

#         # ----------------------------------------------------
#         # 2) DETERMINE CURRENCY PAIR
#         # ----------------------------------------------------
#         # currency_pair = (
#         #     meta.get("currency_pair")
#         #     or meta.get("currencyPair")
#         #     or getattr(quote_obj, "currencyPair", None)
#         #     or "XAU/INR"  # default gold
#         # )



#         currency_pair = meta.get("currencyPair")

#         # Fallback ONLY to Quote table
#         if not currency_pair:
#             currency_pair = getattr(quote_obj, "currencyPair", None)

#         # If still missing → abort (do NOT default to gold)
#         if not currency_pair:
#             logger.warning("Missing currencyPair; cannot determine metal.")
#             return False

#         # currency_pair = (
#         #     meta.get("currencyPair")
#         #     or meta.get("currency_pair")
#         #     or (quote_obj.currencyPair if quote_obj else None)
#         # )

#         # # FINAL fallback based on metal
#         # if not currency_pair:
#         #     metal = meta.get("metal") or (quote_obj.metal if quote_obj else None)
#         #     if metal == "GOLD":
#         #         currency_pair = "XAU/INR"
#         #     elif metal == "SILVER":
#         #         currency_pair = "XAG/INR"

#         # if not currency_pair:
#         #     logger.error("currencyPair still missing — aborting balance update")
#         #     return False


#         # ----------------------------------------------------
#         # 3) GET customerRefNo
#         # ----------------------------------------------------
#         custRefNo = (
#             meta.get("customerRefNo")
#             or meta.get("custRefNo")
#             or getattr(quote_obj, "customerRefNo", None)
#         )

#         # try profile
#         if not custRefNo and getattr(payment_record, "user", None) and Profile is not None:
#             try:
#                 p = Profile.objects.filter(user=payment_record.user).first()
#                 if p and getattr(p, "customerRefNo", None):
#                     custRefNo = p.customerRefNo
#             except Exception:
#                 logger.exception("Profile lookup failed for custRefNo")

#         # no custRefNo = cannot continue
#         if not custRefNo:
#             logger.warning("Missing custRefNo; cannot update Balance.")
#             return False

#         # ----------------------------------------------------
#         # 4) CUSTOMER NAME / KYC
#         # ----------------------------------------------------
#         customerName = (
#             meta.get("customerName")
#             or (quote_obj.customerName if quote_obj and getattr(quote_obj, "customerName", None) else None)
#         )

#         kyc_status = (
#             meta.get("kyc_status")
#             or (quote_obj.kyc_status if quote_obj and getattr(quote_obj, "kyc_status", None) else None)
#         )

#         if (not customerName or not kyc_status) and getattr(payment_record, "user", None) and Profile is not None:
#             try:
#                 p = Profile.objects.filter(user=payment_record.user).first()
#                 if p:
#                     customerName = customerName or getattr(p, "name", None) or getattr(p, "customerName", None) or str(p.user)
#                     kyc_status = kyc_status or getattr(p, "kyc_status", None)
#             except Exception:
#                 logger.exception("Profile lookup failed for customerName/kyc")

#         # ----------------------------------------------------
#         # 5) UPDATE / CREATE BALANCE
#         # ----------------------------------------------------
#         try:
#             existing = Balance.objects.filter(custRefNo=custRefNo, currency_pair=currency_pair).first()

#             if existing:
#                 # increment existing balance
#                 existing.bal_quantity = (existing.bal_quantity or Decimal("0")) + qty
#                 existing.customerName = customerName or existing.customerName
#                 existing.kyc_status = kyc_status or existing.kyc_status
#                 existing.balance_as_of = timezone.now()
#                 existing.save(update_fields=["bal_quantity", "customerName", "kyc_status", "balance_as_of"])

#                 logger.info(
#                     "Updated Balance: custRefNo=%s pair=%s qty=%s (newTotal=%s)",
#                     custRefNo, currency_pair, qty, existing.bal_quantity
#                 )
#             else:
#                 # create new row
#                 Balance.objects.create(
#                     custRefNo=custRefNo,
#                     customerName=customerName or "",
#                     kyc_status=kyc_status or "",
#                     currency_pair=currency_pair,
#                     bal_quantity=qty,
#                     blocked_quantity=Decimal("0"),
#                     balance_as_of=timezone.now(),
#                     date_created=timezone.now()
#                 )
#                 logger.info(
#                     "Created Balance: custRefNo=%s pair=%s qty=%s",
#                     custRefNo, currency_pair, qty
#                 )

#         except Exception:
#             logger.exception("Failed to create/update Balance for PaymentRecord id=%s", getattr(payment_record, "id", None))
#             return False

#         # ----------------------------------------------------
#         # 6) MARK AS PROCESSED
#         # ----------------------------------------------------
#         meta["balance_created"] = True
#         payment_record.metadata = meta
#         try:
#             payment_record.save(update_fields=["metadata"])
#         except Exception:
#             logger.exception("Failed saving metadata for PaymentRecord id=%s", getattr(payment_record, "id", None))

#         return True

#     except Exception:
#         logger.exception("Unexpected error in _create_balance_from_payment for PaymentRecord id=%s", getattr(payment_record, "id", None))
#         return False


# def payment_page(request):
#     """
#     Renders the payment page. Expects session keys:
#       - payment_amount (int, paise)
#       - payment_quote_id
#     """
#     amount_paise = request.session.get('payment_amount')
#     quote_id = request.session.get('payment_quote_id')

#     if not amount_paise:
#         messages.error(request, "No payment information found.")
#         return redirect('/')  # change to an appropriate page if needed

#     context = {
#         "amount_in_paise": amount_paise,
#         "amount": (Decimal(amount_paise) / Decimal(100)) if amount_paise else None,
#         "quote_id": quote_id,
#         "razorpay_key_id": getattr(settings, "RAZORPAY_KEY_ID", ""),
#     }
#     return render(request, 'app_pay/payment_page.html', context)


# def create_order(request):
#     """
#     POST /payments/create-order/
#     Expects: amount (int, paise) in POST or fallback to session.
#     Returns JSON: { "id": "<razorpay_order_id>" }
#     """
#     if request.method != 'POST':
#         return HttpResponseBadRequest("Only POST allowed")

#     amount_raw = request.POST.get('amount') or request.session.get('payment_amount')
#     try:
#         amount = int(amount_raw)
#     except Exception as e:
#         logger.exception("create_order: invalid amount '%s' -> %s", amount_raw, e)
#         return JsonResponse({'error': 'invalid_amount', 'message': str(e)}, status=400)

#     client = get_razorpay_client()
#     if client is None:
#         msg = "Razorpay client not configured"
#         logger.error(msg)
#         return JsonResponse({'error': 'client_init_failed', 'message': msg}, status=500)

#     try:
#         order_data = {
#             "amount": amount,
#             "currency": "INR",
#             "payment_capture": 1,
#             "receipt": f"quote_{request.session.get('payment_quote_id') or ''}"
#         }
#         razor_order = client.order.create(order_data)

#         print("DEBUG (create_order) → buy_quantity =", request.session.get("buy_quantity"))
#         print("DEBUG (create_order) → currency_pair =", request.session.get("currency_pair"))
#         print("DEBUG (create_order) → payment_customerRefNo =", request.session.get("payment_customerRefNo"))

#         # Persist a PaymentRecord for correlation (best-effort)
#         try:
#             pr = PaymentRecord.objects.create(
#             user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
#             quote_id=request.session.get('payment_quote_id'),
#             razorpay_order_id=razor_order.get('id'),
#             amount_paise=razor_order.get('amount'),
#             amount=(Decimal(razor_order.get('amount')) / Decimal(100)) if razor_order.get('amount') else None,
#             status="created",
#             metadata={
#                 "razor_order": razor_order,
#                 "quantity": request.session.get("buy_quantity"),
#                 "currency_pair": request.session.get("currency_pair"),
#                "customerRefNo": request.session.get("payment_customerRefNo"),
#             }
#         )

#             logger.debug("Created PaymentRecord id=%s for razor_order=%s", pr.id, razor_order.get('id'))
#         except Exception as e:
#             logger.exception("Failed to persist PaymentRecord at create_order: %s", e)

#         return JsonResponse({'id': razor_order.get('id')})
#     except Exception as exc:
#         logger.exception("create_order: Razorpay order creation failed: %s", exc)
#         return JsonResponse({'error': 'razorpay_failed', 'message': str(exc)}, status=500)


# @csrf_exempt
# def razorpay_webhook(request):
#     """
#     Webhook endpoint — verify signature using RAZORPAY_WEBHOOK_SECRET.
#     On capture it will create/update PaymentRecord (already present) and update Balance.
#     """
#     webhook_secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", None)
#     payload = request.body
#     received_sig = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')

#     if not webhook_secret:
#         logger.error("Webhook secret not configured")
#         return HttpResponseBadRequest("Webhook secret not configured")

#     expected_sig = hmac.new(webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
#     if not hmac.compare_digest(expected_sig, received_sig or ""):
#         logger.warning("Invalid webhook signature. expected=%s received=%s", expected_sig, received_sig)
#         return HttpResponseBadRequest("Invalid signature")

#     try:
#         event = json.loads(payload)
#     except Exception as e:
#         logger.exception("Invalid webhook payload: %s", e)
#         return HttpResponseBadRequest("Invalid payload")

#     event_type = event.get("event")
#     logger.info("Razorpay webhook received: %s", event_type)

#     payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {}) or {}
#     order_id = payment_entity.get("order_id")
#     payment_id = payment_entity.get("id")
#     status = payment_entity.get("status")
#     amount = payment_entity.get("amount")  # paise

#     try:
#         pr = None
#         if payment_id:
#             pr = PaymentRecord.objects.filter(razorpay_payment_id=payment_id).first()
#         if not pr and order_id:
#             pr = PaymentRecord.objects.filter(razorpay_order_id=order_id).first()

#         if pr is None:
#             pr = PaymentRecord.objects.create(
#                 user=None,
#                 quote_id=None,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_id=payment_id,
#                 amount_paise=amount,
#                 amount=(Decimal(amount) / Decimal(100)) if amount else None,
#                 status=(status or "pending"),
#                 metadata={"raw_event": event}
#             )
#             logger.info("Webhook created new PaymentRecord id=%s for event %s", pr.id, event_type)
#         else:
#             updated = False
#             if payment_id and not pr.razorpay_payment_id:
#                 pr.razorpay_payment_id = payment_id
#                 updated = True
#             if order_id and not pr.razorpay_order_id:
#                 pr.razorpay_order_id = order_id
#                 updated = True
#             if amount and not pr.amount_paise:
#                 pr.amount_paise = amount
#                 try:
#                     pr.amount = Decimal(amount) / Decimal(100)
#                 except (InvalidOperation, TypeError):
#                     pass
#                 updated = True
#             if status:
#                 pr.status = status
#                 updated = True
#             meta = pr.metadata or {}
#             meta.update({"last_webhook_event": event_type})
#             pr.metadata = meta
#             if updated:
#                 pr.save()
#                 logger.debug("Updated PaymentRecord id=%s from webhook %s", pr.id, event_type)

#         # If this is a capture/authorized event, attempt to create/update Balance
#         try:
#             if getattr(pr, "status", "").lower() in ("captured", "authorized"):
#                 _create_balance_from_payment(pr)
#         except Exception:
#             logger.exception("Failed to create balance from webhook for PaymentRecord id=%s", getattr(pr, "id", None))

#     except Exception as e:
#         logger.exception("Failed to create/update PaymentRecord from webhook: %s", e)

#     return HttpResponse(status=200)


# def execute_mmtc_order(request, payment_record):
#     print("🔥 execute_mmtc_order CALLED")

#     """
#     Calls MMTCP: /trade/executeOrderPartnerPg
#     Final step after Razorpay payment success.
#     Uses data from Quote table + PaymentRecord session metadata.
#     """
#     try:
#         # -------------------------------
#         # 1) Load quote details
#         # -------------------------------
#         quote_obj = None
#         if Quote is not None and payment_record.quote_id:
#             quote_obj = Quote.objects.filter(quoteId=payment_record.quote_id).first()

#         if not quote_obj:
#             return {"error": True, "message": "Quote not found for execute order"}

#         # -------------------------------
#         # 2) Extract all required fields
#         # -------------------------------
#         custRefNo = quote_obj.customerRefNo
#         quoteId = quote_obj.quoteId
#         quantity = quote_obj.quantity
#         preTaxAmount = quote_obj.preTaxAmt
#         totalAmount = quote_obj.totalAmt
#         tax1Amt = quote_obj.tax1Amt or "0.00"
#         tax2Amt = quote_obj.tax2Amt or "0.00"

#         # from validation step
#         transaction_ref = quote_obj.transactionOrderID
#         transaction_date = quote_obj.createdAt

#         # --------------------------------
#         # 3) Billing address (MMTCP requires it)
#         # --------------------------------
#         profile = None
#         billing_address_id = None
#         try:
#             profile = Profile.objects.filter(user=payment_record.user).first()
#             if profile:
#                 billing_address_id = profile.billingAddressId  # MUST exist
#         except Exception as e:
#             logger.warning("Billing address fetch failed: %s", e)


#             # -------------------------------
#             # PRE-EXECUTE GUARD (MANDATORY)
#             # -------------------------------
#         if not profile:
#             return {"error": True, "message": "Profile not found"}

#         if not profile.dgcustomerRefNo:
#             return {"error": True, "message": "DG Customer Ref missing"}
            
#         if not profile.billingAddressId or not profile.deliveryAddressId:
#             return {
#             "error": True,
#             "message": "MMTC Address IDs missing. Re-fetch profile before execute."
#         }
#         ##################remove this from here
#         print(
#             "🧪 PROFILE CHECK →",
#             "dg:", getattr(profile, "dgcustomerRefNo", None),
#             "bill:", getattr(profile, "billingAddressId", None),
#             "del:", getattr(profile, "deliveryAddressId", None),
#         )


#         # if not billing_address_id:
#         #     return {"error": True, "message": "Billing Address ID missing in Profile"}

#         payload = {
#             "dgCustomerRefNo": profile.dgcustomerRefNo,
#             "customerRefNo": profile.customerRefNo,
#             "calculationType": "Q",
#             "billingAddressId": billing_address_id,
#             "deliveryAddressId": profile.deliveryAddressId,
#             "preTaxAmount": str(preTaxAmount),
#             "quantity": str(quantity),
#             "quoteId": quoteId, 
#             "tax1Amt": str(tax1Amt),
#             "tax2Amt": str(tax2Amt),
#             "taxAmount": str(Decimal(tax1Amt) + Decimal(tax2Amt)),
#             "transactionDate": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
#             "transactionOrderID": str(transaction_ref),
#             "totalAmount": str(totalAmount),

#         }
#         print("\n🔥 EXECUTE ORDER PAYLOAD =", payload)

#         # --------------------------------
#         # 5) Call MMTCP API
#         # --------------------------------
#         response = make_post(
#             endpoint="TRADE_EXECUTE_ORDER_PARTNER_PG",
#             payload=payload
#         )

#         print("🔥 EXECUTE ORDER RESPONSE =", response)

#         # --------------------------------
#         # 6) Save MMTCP response to PaymentRecord
#         # --------------------------------
#         meta = payment_record.metadata or {}
#         meta["mmtc_execute_response"] = response
#         payment_record.metadata = meta
#         payment_record.save(update_fields=["metadata"])

#         return response

#     except Exception as e:
#         logger.exception("execute_mmtc_order FAILED: %s", e)
#         return {"error": True, "message": str(e)}


# def payment_success(request):
#     """
#     GET: show success page.
#     POST: verify signature and record payment.
#     Endpoint: /payments/success/
#     """
#     if request.method != 'POST':
#         return render(request, 'app_pay/success.html')

#     razorpay_order_id = request.POST.get('razorpay_order_id')
#     razorpay_payment_id = request.POST.get('razorpay_payment_id')
#     razorpay_signature = request.POST.get('razorpay_signature')
#     quote_id = request.POST.get('quote_id') or request.session.get('payment_quote_id')

#     if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
#         logger.warning(
#             "payment_success missing fields: order=%s payment=%s signature=%s",
#             razorpay_order_id, razorpay_payment_id, bool(razorpay_signature)
#         )
#         return HttpResponseBadRequest("Missing payment data")

#     client = get_razorpay_client()
#     if client is None:
#         logger.error("payment_success called but razorpay client not configured")
#         return HttpResponseServerError("Payment configuration error")

#     # -----------------------------
#     # 1️⃣ VERIFY RAZORPAY SIGNATURE
#     # -----------------------------
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpay_signature
#         })
#     except razorpay.errors.SignatureVerificationError:
#         return HttpResponseBadRequest("Signature verification failed")
#     except Exception as e:
#         logger.exception("Unexpected verification error: %s", e)
#         return HttpResponseServerError("Verification error")

#     # -----------------------------
#     # 2️⃣ Get Payment Amount
#     # -----------------------------
#     amount_paise = request.session.get('payment_amount')

#     if amount_paise is None:
#         try:
#             order = client.order.fetch(razorpay_order_id)
#             amount_paise = order.get("amount")
#         except Exception:
#             amount_paise = None

#     amount_inr = None
#     try:
#         if amount_paise:
#             amount_inr = Decimal(amount_paise) / Decimal(100)
#     except Exception:
#         amount_inr = None

#     # -----------------------------
#     # 3️⃣ CREATE / UPDATE PaymentRecord
#     # -----------------------------
#     pr = (
#         PaymentRecord.objects.filter(razorpay_order_id=razorpay_order_id).first()
#         or PaymentRecord.objects.filter(razorpay_payment_id=razorpay_payment_id).first()
#     )

#     # 🔒 DUPLICATE EXECUTION GUARD
#     meta = pr.metadata or {}
#     if meta.get("finalized"):
#         logger.warning("Payment already finalized. Skipping execution.")
#         return render(request, "app_pay/success.html", {"payment_record": pr})

#     # --- CASE A: FIRST-TIME RECORD ---
#     if pr is None:
#         pr = PaymentRecord.objects.create(
#             user=request.user if request.user.is_authenticated else None,
#             quote_id=quote_id,
#             razorpay_order_id=razorpay_order_id,
#             razorpay_payment_id=razorpay_payment_id,
#             amount_paise=amount_paise,
#             amount=amount_inr,
#             status="captured",
#             metadata={"via": "payment_success_post"}
#         )

#         try:
#             execute_mmtc_order(request, pr)
#         except Exception:
#             logger.exception("MMTC execution failed")

#     # --- CASE B: EXISTING PaymentRecord ---
#     else:
#         pr.razorpay_payment_id = pr.razorpay_payment_id or razorpay_payment_id
#         pr.amount_paise = pr.amount_paise or amount_paise
#         if amount_inr and not pr.amount:
#             pr.amount = amount_inr

#         pr.status = "captured"
#         pr.quote_id = pr.quote_id or quote_id

#         meta = pr.metadata or {}
#         meta.update({"last_updated_via": "payment_success_post"})
#         pr.metadata = meta
#         pr.save()

#         try:
#             execute_mmtc_order(request, pr)
#         except Exception:
#             logger.exception("MMTC execution failed")

#     # -----------------------------
#     # 4️⃣ INJECT CRITICAL METADATA FOR SILVER/GOLD
#     # -----------------------------
#     try:
#         quote_obj = Quote.objects.filter(quoteId=pr.quote_id).first()
#         meta = pr.metadata or {}

#         if quote_obj:
#             # correct currency pair
#             meta["currencyPair"] = quote_obj.currencyPair

#             # correct metal type
#             if "XAG" in quote_obj.currencyPair:
#                 meta["metalType"] = "SILVER"
#             else:
#                 meta["metalType"] = "GOLD"

#             # correct quantity
#             meta["quantity"] = str(quote_obj.quantity)

#             # ensure customerRefNo
#             meta["customerRefNo"] = quote_obj.customerRefNo

#             pr.metadata = meta
#             pr.save(update_fields=["metadata"])

#             logger.info("🔥 Injected metadata: %s", meta)

#     except Exception:
#         logger.exception("Metadata injection failed")

#     # -----------------------------
#     # 5️⃣ UPDATE BALANCE TABLE
#     # -----------------------------
#     try:
#         if pr.status.lower() in ("captured", "authorized"):
#             _create_balance_from_payment(pr)
#     except Exception:
#         logger.exception("Balance update failed")

#     # -----------------------------
#     # 6️⃣ CREATE HOLDING RECORD (GOLD OR SILVER)
#     # -----------------------------
#     try:
#         from app_shop.models import Holding
#         user = pr.user
#         if user:
#             meta = pr.metadata or {}

#             weight = None
#             if meta.get("quantity"):
#                 try:
#                     weight = Decimal(str(meta["quantity"]))
#                 except:
#                     weight = None

#             if weight:
#                 metal_type = meta.get("metalType", "GOLD")
#                 price_per_gram = pr.amount / weight if pr.amount else Decimal("0")

        
#                 # Holding.objects.create(
#                 #     user=user,
#                 #     metal_type=metal_type,
#                 #     weight=weight,
#                 #     price_per_gram=price_per_gram,
#                 #     total_price=pr.amount
#                 # )
#                 # logger.info("🔥 Holding created → %s %sg", metal_type, weight)

#                 # 🔒 PREVENT DUPLICATE HOLDING CREATION
#                 if not pr.metadata.get("holding_created"):
#                     Holding.objects.create(
#                 user=user,
#                 metal_type=metal_type,
#                 weight=weight,
#                 price_per_gram=price_per_gram,
#                     total_price=pr.amount
#             )

#             meta = pr.metadata or {}
#             meta["holding_created"] = True
#             pr.metadata = meta
#             pr.save(update_fields=["metadata"])
#         else:
#             logger.warning("Holding already created for PaymentRecord id=%s", pr.id)


#     except Exception:
#         logger.exception("Holding creation failed")

#     # -----------------------------
#     # 7️⃣ CLEAR SESSION
#     # -----------------------------
#     # 🔒 STEP-2: MARK PAYMENT AS FINALIZED (ONE-TIME)
#     meta = pr.metadata or {}
#     meta["finalized"] = True
#     pr.metadata = meta
#     pr.save(update_fields=["metadata"])

#     request.session.pop('payment_amount', None)
#     request.session.pop('payment_quote_id', None)
#     request.session.pop('payment_customerRefNo', None)

#     return render(request, 'app_pay/success.html', {"payment_record": pr})

# # ----------------------
# # Helper: server-side payment (placeholder)
# # ----------------------
# def process_payment_server_side(body: dict) -> dict:
#     """
#     Placeholder for server-side payment capture if you support server-side gateway payments.
#     If you don't use server-side capture, remove or implement to call your payment provider.
#     Return a dict e.g. {"success": True, "provider": "razorpay", "payment_id": "...", ...}
#     """
#     # Example: if you wanted to charge using Razorpay server-side (create payment_id via Orders API or capture),
#     # you could implement it here using get_razorpay_client(). For now, return failure so 'our_pg' isn't used accidentally.
#     return {"success": False, "message": "Server-side payment not implemented."}








# app_pay/views.py
import json
import hmac
import hashlib
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponse,
    HttpResponseServerError,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from app_shop.models import Transaction
import razorpay

from app_shop.utils import make_post
from .models import PaymentRecord

logger = logging.getLogger(__name__)

from app_shop.models import Balance

try:
    from app_trade.models import Quote
except Exception:
    Quote = None

try:
    from app_user.models import Profile
except Exception:
    Profile = None


# -------------------------------------------------
# Razorpay client
# -------------------------------------------------
def get_razorpay_client():
    try:
        key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)
        if not key_id or not key_secret:
            logger.error("Razorpay keys missing")
            return None
        return razorpay.Client(auth=(key_id, key_secret))
    except Exception:
        logger.exception("Razorpay client init failed")
        return None


# -------------------------------------------------
# Balance creation (BUY)
# -------------------------------------------------
def _create_balance_from_payment(payment_record):
    """
    Create / update Balance from a successful BUY payment.

    SAFE GUARANTEES:
    - balance_created is set ONLY if DB write succeeds
    - function is idempotent
    - supports retry / recovery
    """

    try:
        # ----------------------------
        # 0) BASIC GUARDS
        # ----------------------------
        if not payment_record:
            return False

        if payment_record.status not in ("captured", "authorized"):
            logger.warning(
                "Balance skip: invalid status %s for PaymentRecord id=%s",
                payment_record.status,
                payment_record.id,
            )
            return False

        meta = payment_record.metadata or {}

        # Do NOT early-return on balance_created blindly
        # We verify actual DB state first
        balance_already_marked = meta.get("balance_created", False)

        # ----------------------------
        # 1) QUANTITY (MANDATORY)
        # ----------------------------
        qty = None
        if meta.get("quantity") is not None:
            try:
                qty = Decimal(str(meta["quantity"]))
            except Exception:
                qty = None

        if not qty or qty <= Decimal("0"):
            logger.error(
                "Balance abort: invalid quantity=%s for PaymentRecord id=%s",
                meta.get("quantity"),
                payment_record.id,
            )
            return False

        # ----------------------------
        # 2) CURRENCY PAIR (MANDATORY)
        # ----------------------------
        currency_pair = meta.get("currencyPair")
        if not currency_pair:
            logger.error(
                "Balance abort: missing currencyPair for PaymentRecord id=%s",
                payment_record.id,
            )
            return False

        # ----------------------------
        # 3) CUSTOMER REF NO (MANDATORY)
        # ----------------------------
        custRefNo = meta.get("customerRefNo")
        if not custRefNo and payment_record.user:
            from app_user.models import Profile
            profile = Profile.objects.filter(user=payment_record.user).first()
            if profile:
                custRefNo = profile.customerRefNo

        if not custRefNo:
            logger.error(
                "Balance abort: missing customerRefNo for PaymentRecord id=%s",
                payment_record.id,
            )
            return False

        # ----------------------------
        # 4) GET / CREATE BALANCE ROW
        # ----------------------------
        from app_shop.models import Balance

        balance = Balance.objects.filter(
            custRefNo=custRefNo,
            currency_pair=currency_pair,
        ).first()

        if balance:
            # Already exists → increment safely
            balance.bal_quantity = (balance.bal_quantity or Decimal("0")) + qty
            balance.balance_as_of = timezone.now()
            balance.save(
                update_fields=["bal_quantity", "balance_as_of"]
            )

            logger.info(
                "Balance UPDATED: custRefNo=%s pair=%s +%s (new=%s)",
                custRefNo,
                currency_pair,
                qty,
                balance.bal_quantity,
            )

        else:
            # Create new balance row
            balance = Balance.objects.create(
                custRefNo=custRefNo,
                currency_pair=currency_pair,
                bal_quantity=qty,
                blocked_quantity=Decimal("0"),
                balance_as_of=timezone.now(),
                date_created=timezone.now(),
            )

            logger.info(
                "Balance CREATED: custRefNo=%s pair=%s qty=%s",
                custRefNo,
                currency_pair,
                qty,
            )

        # ----------------------------
        # 5) MARK PAYMENT AS PROCESSED
        # ----------------------------
        # Mark ONLY after DB write succeeded
        if not balance_already_marked:
            meta["balance_created"] = True
            payment_record.metadata = meta
            payment_record.save(update_fields=["metadata"])

        return True

    except Exception as e:
        logger.exception(
            "Balance creation FAILED for PaymentRecord id=%s : %s",
            getattr(payment_record, "id", None),
            e,
        )
        return False
# -------------------------------------------------
# Payment page
# -------------------------------------------------
def execute_mmtc_order(payment_record):
    """
    Calls MMTC EXECUTE ORDER API.
    This MUST run after payment is captured.
    """

    logger.warning(
        "MMTC EXECUTE START | payment_record_id=%s | quote_id=%s",
        payment_record.id,
        payment_record.quote_id,
    )

    if not Quote or not Profile:
        logger.error("MMTC EXECUTE ABORT: Quote/Profile model missing")
        return None

    quote = Quote.objects.filter(quoteId=payment_record.quote_id).first()
    if not quote:
        logger.error("MMTC EXECUTE ABORT: Quote not found")
        return None

    profile = Profile.objects.filter(user=payment_record.user).first()
    if not profile:
        logger.error("MMTC EXECUTE ABORT: Profile not found")
        return None

    # HARD GUARDS (MMTC requirements)
    if not profile.dgcustomerRefNo:
        logger.error("MMTC EXECUTE ABORT: dgcustomerRefNo missing")
        return None

    if not profile.billingAddressId or not profile.deliveryAddressId:
        logger.error("MMTC EXECUTE ABORT: Address IDs missing")
        return None

    payload = {
        "dgCustomerRefNo": profile.dgcustomerRefNo,
        "customerRefNo": profile.customerRefNo,
        "calculationType": "Q",
        "billingAddressId": profile.billingAddressId,
        "deliveryAddressId": profile.deliveryAddressId,
        "preTaxAmount": str(quote.preTaxAmt),
        "quantity": str(quote.quantity),
        "quoteId": quote.quoteId,
        "tax1Amt": str(quote.tax1Amt),
        "tax2Amt": str(quote.tax2Amt),
        "taxAmount": str(Decimal(quote.tax1Amt) + Decimal(quote.tax2Amt)),
        "transactionDate": quote.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
        "transactionOrderID": quote.transactionOrderID,
        "totalAmount": str(quote.totalAmt),
    }

    logger.warning("MMTC EXECUTE PAYLOAD = %s", payload)

    response = make_post(
        endpoint="TRADE_EXECUTE_ORDER_PARTNER_PG",
        payload=payload,
    )

    logger.warning("MMTC EXECUTE RESPONSE = %s", response)

    # Persist response for audit
    meta = payment_record.metadata or {}
    meta["mmtc_execute_response"] = response
    payment_record.metadata = meta
    payment_record.save(update_fields=["metadata"])

    return response


def payment_page(request):
    amount_paise = request.session.get("payment_amount")
    if not amount_paise:
        messages.error(request, "No payment info")
        return redirect("/")

    return render(
        request,
        "app_pay/payment_page.html",
        {
            "amount_in_paise": amount_paise,
            "amount": Decimal(amount_paise) / Decimal(100),
            "quote_id": request.session.get("payment_quote_id"),
            "razorpay_key_id": getattr(settings, "RAZORPAY_KEY_ID", ""),
        },
    )


# -------------------------------------------------
# Create Razorpay Order
# -------------------------------------------------
def create_order(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        amount = int(request.POST.get("amount") or request.session.get("payment_amount"))
    except Exception:
        return JsonResponse({"error": "invalid_amount"}, status=400)

    client = get_razorpay_client()
    if not client:
        return JsonResponse({"error": "gateway_error"}, status=500)

    order = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
            "receipt": f"quote_{request.session.get('payment_quote_id')}",
        }
    )

    PaymentRecord.objects.create(
        user=request.user if request.user.is_authenticated else None,
        quote_id=request.session.get("payment_quote_id"),
        razorpay_order_id=order["id"],
        amount_paise=order["amount"],
        amount=Decimal(order["amount"]) / Decimal(100),
        status="created",
        metadata={
            "quantity": request.session.get("buy_quantity"),
            "currencyPair": request.session.get("currency_pair"),
            "customerRefNo": request.session.get("payment_customerRefNo"),
        },
    )

    return JsonResponse({"id": order["id"]})


# -------------------------------------------------
# Razorpay Webhook
# -------------------------------------------------
@csrf_exempt
def razorpay_webhook(request):
    secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", None)
    if not secret:
        return HttpResponseBadRequest("Webhook not configured")

    payload = request.body
    sig = request.META.get("HTTP_X_RAZORPAY_SIGNATURE")

    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig or ""):
        return HttpResponseBadRequest("Invalid signature")

    event = json.loads(payload)
    entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = entity.get("order_id")
    payment_id = entity.get("id")
    status = entity.get("status")
    amount = entity.get("amount")

    pr = (
        PaymentRecord.objects.filter(razorpay_payment_id=payment_id).first()
        or PaymentRecord.objects.filter(razorpay_order_id=order_id).first()
    )

    if not pr:
        pr = PaymentRecord.objects.create(
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            amount_paise=amount,
            amount=Decimal(amount) / Decimal(100),
            status=status or "pending",
            metadata={"raw_event": event},
        )
    else:
        if payment_id and not pr.razorpay_payment_id:
            pr.razorpay_payment_id = payment_id
        pr.status = status or pr.status
        pr.save(update_fields=["razorpay_payment_id", "status"])

    if pr.status == "captured":
        _create_balance_from_payment(pr)

    return HttpResponse(status=200)


# -------------------------------------------------
# Payment success (FIXED)
# -------------------------------------------------
def payment_success(request):
    if request.method != "POST":
        return render(request, "app_pay/success.html")

    client = get_razorpay_client()
    if not client:
        return HttpResponseServerError("Payment gateway not configured")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    # -----------------------------
    # 1️⃣ VERIFY SIGNATURE
    # -----------------------------
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })
    except Exception:
        return HttpResponseBadRequest("Signature verification failed")

    # -----------------------------
    # 2️⃣ FETCH PAYMENT RECORD
    # -----------------------------
    pr = PaymentRecord.objects.filter(
        razorpay_order_id=razorpay_order_id
    ).first()

    if not pr:
        return HttpResponseBadRequest("Payment record not found")

    meta = pr.metadata or {}

    # 🔒 DUPLICATE GUARD
    if meta.get("finalized"):
        return render(request, "app_pay/success.html", {"payment_record": pr})

    # -----------------------------
    # 3️⃣ SAVE PAYMENT ID + STATUS
    # -----------------------------
    if not pr.razorpay_payment_id:
        pr.razorpay_payment_id = razorpay_payment_id

    pr.status = "captured"
    pr.save(update_fields=["razorpay_payment_id", "status"])

    # -----------------------------
    # 4️⃣ INJECT QUOTE METADATA
    # -----------------------------
    if Quote:
        quote = Quote.objects.filter(quoteId=pr.quote_id).first()
        if quote:
            meta.update({
                "currencyPair": quote.currencyPair,
                "quantity": str(quote.quantity),
                "customerRefNo": quote.customerRefNo,
            })

    pr.metadata = meta
    pr.save(update_fields=["metadata"])

    # -----------------------------
    # 5️⃣ UPDATE BALANCE
    # -----------------------------
    _create_balance_from_payment(pr)

    # -----------------------------
    # 6️⃣ EXECUTE MMTC (ONE TIME)
    # -----------------------------
    if not meta.get("mmtc_executed"):
        response = execute_mmtc_order(pr)

        if response and response.get("status") == 200:
            data = response.get("data", {})
            order = data.get("orderId", {})

            Transaction.objects.get_or_create(
            orderId=order.get("orderId"),
            defaults={
                "customerRefNo": pr.metadata.get("customerRefNo"),
                "user": pr.user,
                "transactionType": "BUY",
                "currencyPair": pr.metadata.get("currencyPair"),
                "quantity": Decimal(pr.metadata.get("quantity")),
                "totalAmt": pr.amount,
                "transactionDate": timezone.now(),
                "status": "EXECUTED",
            }
        )


            meta["mmtc_transaction_id"] = order.get("transactionId")
            meta["mmtc_order_id"] = order.get("orderId")
            meta["mmtc_invoice_id"] = order.get("invoiceId")
            meta["mmtc_executed"] = True

            pr.metadata = meta
            pr.save(update_fields=["metadata"])

    # -----------------------------
    # 7️⃣ FINALIZE (LOCK)
    # -----------------------------
    meta["finalized"] = True
    pr.metadata = meta
    pr.save(update_fields=["metadata"])

    # -----------------------------
    # 8️⃣ CLEAR SESSION
    # -----------------------------
    for k in ("payment_amount", "payment_quote_id", "payment_customerRefNo"):
        request.session.pop(k, None)

    return render(request, "app_pay/success.html", {"payment_record": pr})
