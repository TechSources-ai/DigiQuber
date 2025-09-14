import os
import json
import requests
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from app_user.models import Profile
from django.contrib import messages
from .models import APIToken, Balance
from django.shortcuts import render, redirect
from .utils import auth_api, make_post, get_token

def buy_now_view(request):
    if not request.user.is_authenticated:
        return redirect('signin')  # Use your login URL name

    token_obj = get_token()
    print("Using token to get price:", token_obj.token)

    gold_price = make_post(token_obj.token, 'GOLD_PRICE_ENDPOINT', {"timeFrame": "1D"})

    if gold_price:
        try:
            request_data = json.loads(gold_price)
            if isinstance(request_data, list) and request_data:
                price = request_data[0].get('buy_pretax')
            else:
                price = None
        except Exception as e:
            price = None
            print("JSON decode error:", e)
    else:
        price = None

    print(gold_price, price)
    # Token is now available, proceed to product page
    return render(request, 'app_shop/product_page.html', {'price': price})

def product_page_view(request):
    return render(request, 'app_shop/product_page.html')

def customer_detail(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    custRefNo = Profile.objects.get(user=request.user).customerRefNo
    print("Customer Ref No:", custRefNo)
    balances = Balance.objects.filter(custRefNo=custRefNo)
    print("Balances fetched:", balances)

    context = {
        'balances': balances
    }

    return render(request, 'app_shop/balance.html', context)

def refresh_balance(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    token_obj = get_token()
    # print("Using token to get price:", token_obj.token)
    custRefNo = Profile.objects.get(user=request.user).customerRefNo
    # print("Customer Ref No:", custRefNo)
    balance = make_post(token_obj.token, 'PORTFOLIO_ENDPOINT', {"customerRefNo": custRefNo})

    if balance:
        try:
            request_data = json.loads(balance)
            customer_name = request_data.get("customerName")
            kyc_status = request_data.get("kycStatus")
            balances = request_data.get("balances", [])
            for balance in balances:
                bal_quantity = balance.get("balQuantity")
                currency_pair = balance.get("currencyPair")
                blocked_quantity = balance.get("blockedQuantity")

                Balance.objects.create(
                        custRefNo=custRefNo,
                        customerName=customer_name,
                        kyc_status=kyc_status,
                        currency_pair=currency_pair,
                        bal_quantity=Decimal(bal_quantity),
                        blocked_quantity=Decimal(blocked_quantity)
                    )
            messages.success(request, "Balance data refreshed successfully!")

        except Exception as e:
            print("JSON decode error:", e)
    else:
        messages.success(request, "No Portfolio data found.")

    return redirect('balance', custRefNo=request.user.id)  # Redirect to the balance view with the user's ID