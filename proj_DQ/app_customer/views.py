# app_customer/views.py
import requests
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from .models import Profile
from .forms import EmailForm, ProfileForm
from .utils import auth_api
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def send_confirmation_email(request, email):
    uid = urlsafe_base64_encode(force_bytes(email))
    token = signer.sign(email)
    confirmation_link = f"{settings.SITE_URL}{reverse('confirm_email')}?uid={uid}&token={token}"

    send_mail(
        subject="Confirm your login",
        message=f"Click here to login: {confirmation_link}",
        from_email=None,
        recipient_list=[email],
    )

def email_entry_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            send_confirmation_email(request, email)
            return render(request, 'app_customer/link_sent.html', {'email': email})
    else:
        form = EmailForm()
    return render(request, 'app_customer/email_entry.html', {'form': form})

def confirm_email_view(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')
    email = force_str(urlsafe_base64_decode(uidb64))

    try:
        original_email = signer.unsign(token, max_age=600)  # 10 min expiry
    except SignatureExpired:
        messages.error(request, "Confirmation link expired.")
        return redirect('email_entry')
    except BadSignature:
        messages.error(request, "Invalid confirmation link.")
        return redirect('email_entry')

    if original_email != email:
        messages.error(request, "Email mismatch.")
        return redirect('email_entry')

    user, created = User.objects.get_or_create(email=email, defaults={"username": email})
    login(request, user)

    Profile.objects.get_or_create(user=user)
    profile = user.profile

    if not profile.aadhar_number or not profile.pan_number:  # Mandatory field check
        return redirect('create_profile')
    return redirect('dashboard')

def create_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'app_customer/create_profile.html', {'form': form})

def dashboard_view(request):
    return render(request, 'app_customer/dashboard.html')

def authenticate_with_api(request):
    auth_status, auth_res = auth_api()

    if auth_status == 200:
        print("Authentication successful")
        print(auth_res)
        return redirect('dashboard')
    else:
        return redirect('email_entry')

def create_customer(request):
    sessionId = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXJ0bmVyX2lkIjoidGVjaF9zb3VyY2VzIiwiaWF0IjoxNzU1OTQzNDI4fQ.ynnzFVf9vDGqL43qsrWo6xD_TlnTQ2QrT9c4kocbAIQ'
    url = 'https://cemuat.mmtcpamp.com/customer/createProfile'

    headers = {
        'Accept': 'application/json',
        'Cookie': f'sessionId={sessionId}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        "mobileNumber": "9999107779",
        "customerRefNo": "1234567899",
        "fullName": "Ritesh kumar",
        "kycStatus": "Y",
        "kycInfo": {
            "nameProofType": "pan",
            "nameProofDocNo": "djehj23659k",
            "addressProofType": "aadhar",
            "addressProofDocNo": "877656656577"
        },
        "partner_id": "tech_sources",
        "deliveryAddress": {
            "line1": "delivery laxmi nagar West Delhi",
            "line2": "Hyderabad",
            "city": "Hyderabad",
            "state": "Hyderabad",
            "zip": 500091,
            "country": "India",
            "mobileNumber": "9718957271",
            "statecode": "12"
        },
        "billingAddress": {
            "line1": "billing laxmi nagar West Delhi",
            "line2": "Hyderabad",
            "city": "Hyderabad",
            "state": "Hyderabad",
            "zip": 500091,
            "country": "India",
            "mobileNumber": "9718957271",
            "statecode": "12"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

