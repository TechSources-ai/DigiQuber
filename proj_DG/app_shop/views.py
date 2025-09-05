import os
import json
import requests
from .utils import auth_api, make_post, get_token
from .models import APIToken
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect

def buy_now_view(request):
    if not request.user.is_authenticated:
        return redirect('signin')  # Use your login URL name

    token_obj = get_token()

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
