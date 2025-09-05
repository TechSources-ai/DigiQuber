from django.shortcuts import render, redirect, get_object_or_404
from app_shop.utils import make_post, auth_api, get_token
from app_user.models import Profile

def createCustomerView(request):
    # Get all users where profile exists and dgcustomerRefNo is null
    customers = Profile.objects.filter(dgcustomerRefNo__isnull=True)
    return render(request, 'app_admin/createCustomer.html', {'customers': customers})

def createProfileView(request, user_id):
    customer = get_object_or_404(Profile, customerRefNo=user_id)
    tokenObj = get_token()
    
    payload={
        "mobileNumber": customer.phone,
        "emailAddress": customer.email,
        "customerRefNo": customer.customerRefNo,
        "fullName": customer.name,
        "kycStatus": customer.kycStatus,
        "kycInfo": {
            "nameProofType": customer.nameProofType,
            "nameProofId": customer.nameProofId,
            "addressProofType": customer.addressProofType,
            "addressProofId": customer.addressProofId,
        },
        "partnerId": "PARTNER123",  # Replace with actual partner ID
        "deliveryAddress": {
            "line1": customer.delivery_address.street,
            "line2": customer.delivery_address.street,
            "city": customer.delivery_address.city,
            "state": customer.delivery_address.state,
            "zip": customer.delivery_address.zip,
            "country": customer.delivery_address.country,
            "mobileNumber": customer.phone,
        },
        "billingAddress": {
            "line1": customer.delivery_address.street,
            "line2": customer.delivery_address.street,
            "city": customer.delivery_address.city,
            "state": customer.delivery_address.state,
            "zip": customer.delivery_address.zip,
            "country": customer.delivery_address.country,
            "mobileNumber": customer.phone,
        },
    }

    resp = make_post(token=tokenObj.token, endpoint='CREATE_PROFILE_ENDPOINT', payload=payload)
    return redirect('users_without_customerid')

