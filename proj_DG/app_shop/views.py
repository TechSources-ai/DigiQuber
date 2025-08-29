import os
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import APIToken
from dotenv import load_dotenv
import requests
from datetime import timedelta

load_dotenv()

TOKEN_VALIDITY_MINUTES = 30  # Set token validity duration as per API docs

def buy_now_view(request):
    if not request.user.is_authenticated:
        return redirect('signin')  # Use your login URL name

    # Check for a valid token
    now = timezone.now()
    valid_since = now - timedelta(minutes=TOKEN_VALIDITY_MINUTES)
    token_obj = APIToken.objects.filter(created_at__gte=valid_since).order_by('-created_at').first()

    if not token_obj:
        # Request new token from API
        partner_id = os.getenv('PARTNER_ID')
        username = os.getenv('API_USERNAME')
        password = os.getenv('API_PASSWORD')
        response = requests.post(
            'https://thirdparty.example.com/api/auth',
            json={
                'partner_id': partner_id,
                'username': username,
                'password': password
            }
        )
        if response.status_code == 200:
            token = response.json().get('token')
            token_obj = APIToken.objects.create(token=token)
        else:
            return render(request, 'app_shop/token_error.html', {'error': response.text})

    # Token is now available, proceed to product page
    return redirect('product_page')  # Use your product page URL name

def product_page_view(request):
    return render(request, 'app_shop/product_page.html')
