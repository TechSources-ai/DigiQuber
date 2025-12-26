from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from app_user.models import Profile
from app_shop.utils import make_post, get_token
import json

import logging
logger = logging.getLogger(__name__)



def prepRequest(request, custRefID):
    customer = get_object_or_404(Profile, customerRefNo=custRefID)
    mobile = customer.user.phone
    refNo = customer.customerRefNo
    if refNo:
        return ("customerRefNo", refNo)
    return ("mobile", mobile)


def parseResp(request, response):
    logger.info("MMTC RESPONSE: %s", response)
    if not response:
        messages.error(request, "MMTC API failed")
        return
    if response.get("status") != 200:
        messages.error(request, response.get("reason", "MMTC error"))
    else:
        messages.success(request, "Operation successful")

@login_required
def manageCustomerView(request):
    customers = Profile.objects.all()
    return render(request, "app_admin/manageCustomer.html", {"customers": customers})


@login_required
def createProfileView(request, user_id):
    customer = get_object_or_404(Profile, customerRefNo=user_id)

    kycStatus = "Y" if customer.kycStatus == 1 else "I"

    payload = {
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

    print("CREATE_PROFILE payload:", json.dumps(payload, indent=2))

    resp = make_post(endpoint="CREATE_PROFILE_ENDPOINT", payload=payload)
    print("CREATE_PROFILE response:", resp)

    if resp and resp.get("status") == 200:
        data = resp.get("data")
        if isinstance(data, list) and len(data) > 0:
            dg_id = data[0].get("dgCustomerRefNo")
            if dg_id:
                customer.dgcustomerRefNo = dg_id
                customer.save()
                messages.success(request, f"DG Customer created: {dg_id}")
                return redirect("manageCustomer")

    messages.error(request, resp.get("reason", "Create profile failed"))
    return redirect("manageCustomer")

@login_required
def fetchProfileView(request, user_id):
    customer = get_object_or_404(Profile, customerRefNo=user_id)
    token = get_token()
    fetchId, fetchVal = prepRequest(request, custRefID=user_id)

    resp = make_post(
        token=token,
        endpoint="GET_PROFILE_ENDPOINT",
        payload={},
        fetchId=fetchId,
        fetchVal=fetchVal,
    )

    print("GET_PROFILE response:", resp)

    if resp and resp.get("status") == 200:
        data = resp.get("data", {})

        # --- Save DG Customer Ref ---
        #remove 451-455
        dg_id = data.get("dgCustomerRefNo")
        if dg_id: 
            customer.dgcustomerRefNo = dg_id

       # --- Save Address IDs (CRITICAL) ---
        billing = data.get("billingAddress", [])
        delivery = data.get("deliveryAddress", [])

        if billing and billing[0].get("id"):
            customer.billingAddressId = billing[0]["id"]

        if delivery and delivery[0].get("id"):
            customer.deliveryAddressId = delivery[0]["id"]

        customer.save(update_fields=[
            "dgcustomerRefNo",
            "billingAddressId",
            "deliveryAddressId",
        ])

        messages.success(
            request,
            "MMTC profile synced (DG ID + Address IDs saved)"
        )
        return redirect("manageCustomer")

    messages.error(request, "Unable to fetch MMTC profile")
    return redirect("manageCustomer")


@login_required
def activateCustomer(request, user_id):
    fetchId, fetchVal = prepRequest(request, custRefID=user_id)
    resp = make_post(endpoint="ACTIVATE_CUSTOMER_ENDPOINT", payload={}, fetchId=fetchId, fetchVal=fetchVal)
    parseResp(request, resp)
    return redirect("manageCustomer")

@login_required
def deActivateCustomer(request, user_id):
    fetchId, fetchVal = prepRequest(request, custRefID=user_id)
    resp = make_post(endpoint="DEACTIVATE_CUSTOMER_ENDPOINT", payload={}, fetchId=fetchId, fetchVal=fetchVal)
    parseResp(request, resp)
    return redirect("manageCustomer")


@login_required
def validateKYC(request, user_id):
    fetchId, fetchVal = prepRequest(request, custRefID=user_id)
    resp = make_post(endpoint="VALIDATE_CUSTOMER_ENDPOINT", payload={}, fetchId=fetchId, fetchVal=fetchVal)
    parseResp(request, resp)
    return redirect("manageCustomer")

@login_required
def inValidateKYC(request, user_id):
    fetchId, fetchVal = prepRequest(request, custRefID=user_id)
    resp = make_post(endpoint="INVALIDATE_CUSTOMER_ENDPOINT", payload={}, fetchId=fetchId, fetchVal=fetchVal)
    parseResp(request, resp)
    return redirect("manageCustomer")

@login_required
def updateDgCustId(request):
    customer = get_object_or_404(Profile, user=request.user)
    #customer.dgcustomerRefNo = "C8K7A75QYG83"  # manual override if needed
    customer.save()
    messages.success(request, "DG Customer ID force-updated")
    return redirect("manageCustomer")
