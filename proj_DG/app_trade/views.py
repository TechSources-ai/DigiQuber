import requests
import razorpay
from django.shortcuts import render, redirect
from decimal import Decimal
from datetime import timedelta

from .models import TradeBuy, Quote
from app_user.models import Profile
from app_shop.api_config import ExternalAPI
from app_shop.utils import make_post, generate_transaction_ref

from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse


def post_login_handler(request):
    next_url = request.session.get('next', '/')
    return redirect(next_url)

def verify_payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')

    try:
        # Check signature validity
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        # Payment is successful
        return JsonResponse({'status': 'success'})
    except razorpay.errors.SignatureVerificationError:
        # Payment failed
        return JsonResponse({'status': 'failure'})

def saveQuote(request, quote_data):
    Quote.objects.create(
            currencyPair=quote_data['currency_pair'],
            basePrice=quote_data['unit-price'],
            quantity=quote_data['quantity'],
            preTaxAmt=quote_data['preTaxAmt'],
            tax1Perc=quote_data['tax1_perc'],
            tax2Perc=quote_data['tax2_perc'],
            sessionKey=request.session.session_key,  # Track session for guest users
            user=quote_data['user'] if 'user' in quote_data else None,  # None if not logged in
            customerRefNo=quote_data['customer_ref_no'] if 'customer_ref_no' in quote_data else None  # None if not logged in
        )

def generate_quote(request):
    ep = 'TRADE_BUY_ENDPOINT'
    if not request.user.is_authenticated:
        return redirect('signin')
    else:
        if request.method == 'POST':
            quote_data = {
                'value': request.POST.get('pta'),
                'currencyPair': request.POST.get('currency-pair'),
                'type': "A"
            }
            profile = Profile.objects.get(user=request.user)
            if not profile.customerRefNo:
                messages.error(request, "Please update your profile for missing information.")
                return redirect('profile')
            else:
                transaction_ref = generate_transaction_ref(profile.customerRefNo, request.session.session_key)
                quote_data['customerRefNo'] = profile.customerRefNo
                quote_data['transactionRefNo'] = transaction_ref
                print(quote_data)
                # saveQuote(request, quote_data)  # Save current quote data to db in Quote model

                response = make_post(
                    endpoint=ep, 
                    payload=quote_data)
                print("Response from Trade Buy API:", response)

            return render(request, 'app_shop/validateQuote.html', {'estimate': response['data']})
    return render(request, 'app_shop/validateQuote.html', {'estimate': response['data']})

def validate_quote(request):
    validate_data = { 
        "customerRefNo": "{{customerRefNo}}", 
        "calculationType": "Q", 
        "preTaxAmount": request.POST.get('pre-tax-amount'),
        "quantity": request.POST.get('quantity'),
        "quoteId": "PTMgyuCtlvNKjK9B1xovWic8a", 
        "tax1Amt": request.POST.get('tax1Perc'),
        "tax2Amt": request.POST.get('tax2Perc'),
        "transactionDate": "2023-03-24T08:51:56.469Z", 
        "transactionOrderID": "3c30177f-1e97-4638-b322-22d0b556dc03", 
        "totalAmount": request.POST.get('pre-tax-amount')
        }

    # print("Quote Data Received for Validation:**************************************")
    # print(quote_data)

    if not request.user.is_authenticated:
        messages.info(request, "Please sign in to proceed with the quote validation.")
        return redirect('signin')  # Or your login/signup route
    elif request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        quote_data['customer_ref_no'] = profile.customerRefNo
        print(quote_data)
        saveQuote(request, quote_data)  # Save current quote data to db in Quote model
        pre_tax_total = Decimal(quote_data['preTaxAmt']) * Decimal(quote_data['quantity'])
        tax1_amt = pre_tax_total * Decimal(quote_data['tax1_perc']) / Decimal(100)
        tax2_amt = pre_tax_total * Decimal(quote_data['tax2_perc']) / Decimal(100)
        total_tax = tax1_amt + tax2_amt
        total_amount = pre_tax_total + total_tax
        isValid, response = make_post(
            endpoint=settings.EXTERNAL_APIS['TRADE_VALIDATE_ENDPOINT_PG'], 
            data=quote_data) 
        return redirect('quote_confirm')
    else:
        return redirect('quote_editor')  # or some other appropriate page

# Payment Page View
def create_order(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    if request.method == "POST":
        amount = 1000  # Amount in paise (₹10)
        currency = "INR"

        # Create an order with Razorpay
        order = client.order.create(dict(
            amount=amount,
            currency=currency,
            payment_capture='1'  # '1' means automatic payment capture
        ))

        order_id = order['id']

        # Pass the order_id and Razorpay key to the front-end
        return JsonResponse({
            'order_id': order_id,
            'razorpay_key': settings.RAZORPAY_KEY_ID
        })

    return render(request, 'payment_page.html')


