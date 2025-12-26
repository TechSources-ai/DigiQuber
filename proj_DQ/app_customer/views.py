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

# def create_profile_view(request):
#     profile = request.user.profile
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')
#     else:
#         form = ProfileForm(instance=profile)
#     return render(request, 'app_customer/create_profile.html', {'form': form})


def create_profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=user)

        if form.is_valid():
            # ---------------------------------
            # 1️⃣ Save profile locally
            # ---------------------------------
            profile = form.save(commit=False)
            profile.user = user

            # ---------------------------------
            # 2️⃣ Ensure addresses already exist
            # (this view assumes edit_profile_view saved them)
            # ---------------------------------
            if not profile.billingAddress or not profile.deliveryAddress:
                return redirect("edit_profile")  # force address completion

            # ---------------------------------
            # 3️⃣ Generate partner-side address ID
            # ---------------------------------
            if not profile.billingAddressId:
                profile.billingAddressId = f"{profile.customerRefNo}_BILL"

            profile.save()

            # ---------------------------------
            # 4️⃣ Sync with MMTC (ONLY ONCE)
            # ---------------------------------
            if not profile.dgcustomerRefNo:
                session_id = request.session.get("mmtc_session_id")

                # If MMTC login not enabled yet, skip sync safely
                if not session_id:
                    return redirect("dashboard")

                payload = {
                    "mobileNumber": user.phone,
                    "customerRefNo": profile.customerRefNo,
                    "fullName": profile.name,
                    "kycStatus": profile.kycStatus,  # "Y" or "I"
                    "partner_id": settings.MMTC_PARTNER_ID,
                    "emailAddress": user.email,
                    "dob": profile.dob.strftime("%Y-%m-%d") if profile.dob else None,
                    "billingAddress": profile.billingAddress,
                    "deliveryAddress": profile.deliveryAddress,
                }

                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Cookie": f"sessionId={session_id}",
                }

                resp = requests.post(
                    settings.MMTC_BASE_URL + "/customer/createProfile",
                    json=payload,
                    headers=headers,
                    timeout=15,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    if "dgCustomerRefNo" in data:
                        profile.dgcustomerRefNo = data["dgCustomerRefNo"]
                        profile.save(update_fields=["dgcustomerRefNo"])
                else:
                    print("MMTC CREATE PROFILE ERROR:", resp.text)

            return redirect("dashboard")

    else:
        form = ProfileForm(instance=profile, user=user)

    return render(
        request,
        "app_customer/create_profile.html",
        {
            "form": form,
        },
    )


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

