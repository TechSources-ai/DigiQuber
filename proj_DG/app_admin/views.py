from app_user.models import Profile
from django.conf import settings
from app_shop.utils import make_post, auth_api, get_token
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def createCustomerView(request):
    # Get all users where profile exists and dgcustomerRefNo is null
    customers = Profile.objects.filter(dgcustomerRefNo__isnull=True)
    return render(request, 'app_admin/createCustomer.html', {'customers': customers})

@login_required
def createProfileView(request, user_id):
    customer = get_object_or_404(Profile, customerRefNo = user_id)
    tokenObj = get_token()
    if customer.kycStatus == 1:
        kycStatus = 'Y'
    else:
        kycStatus = 'N'
    payload={
        "mobileNumber": customer.user.phone,
        "emailAddress": customer.user.email,
        "customerRefNo": customer.customerRefNo,
        "fullName": customer.name,
        "kycStatus": kycStatus,
        "kycInfo": {
            "nameProofType": customer.nameProofType,
            "nameProofId": customer.nameProofId,
            "addressProofType": customer.addressProofType,
            "addressProofId": customer.addressProofId,
        },
        "partner_id": settings.PARTNER_ID,
        "deliveryAddress": customer.deliveryAddress,
        "billingAddress": customer.billingAddress,
    }
    print("Payload:", payload)
    resp = make_post(token=tokenObj.token, endpoint='CREATE_PROFILE_ENDPOINT', payload=payload)
    print(resp)
    if resp:
        try:
            request_data = json.loads(resp)
            if isinstance(request_data, list) and request_data:
                dgCustomerRefNo = request_data[0].get('dgCustomerRefNo')
                if dgCustomerRefNo:
                    customer.dgcustomerRefNo = dgCustomerRefNo
                    customer.save()
            else:
                dgCustomerRefNo = None
        except Exception as e:
            dgCustomerRefNo = None
            print("JSON decode error:", e)
    else:
        dgCustomerRefNo = None
    return redirect('createCustomer')

@login_required
def fetchProfileView(request, user_id):
    customer = get_object_or_404(Profile, customerRefNo = user_id)
    mobile = customer.user.phone
    refNo = customer.customerRefNo
    tokenObj = get_token()
    payload={}
    if refNo is None:
        fetchId = "mobile"
        fetchVal = mobile
    else:
        fetchId = "customerRefNo"
        fetchVal = refNo
    resp = make_post(token=tokenObj.token, endpoint='GET_PROFILE_ENDPOINT', payload=payload, fetchId=fetchId, fetchVal=fetchVal)
    print(resp)
    # if resp:
    #     try:
    #         request_data = json.loads(resp)
    #         if isinstance(request_data, list) and request_data:
    #             dgCustomerRefNo = request_data[0].get('dgCustomerRefNo')
    #             if dgCustomerRefNo:
    #                 customer.dgcustomerRefNo = dgCustomerRefNo
    #                 customer.save()
    #         else:
    #             dgCustomerRefNo = None
    #     except Exception as e:
    #         dgCustomerRefNo = None
    #         print("JSON decode error:", e)
    # else:
    #     dgCustomerRefNo = None
    return redirect('home')
    
def updateDgCustId(request):
    customer = get_object_or_404(Profile, user=3)
    customer.dgcustomerRefNo = "C8K7A75QYG83" # URMH5ERYG172, 7OTY2ZCOE6ST
    customer.save()
    print("Updated")
    return redirect('home')