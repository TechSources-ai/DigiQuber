# import json
# import base64
# import requests
# from .models import APIToken
# from django.utils import timezone
# from django.conf import settings
# from .api_config import ExternalAPI
# from requests.exceptions import RequestException
# from datetime import datetime, timedelta
# import razorpay
# from razorpay.errors import (
#     BadRequestError,
#     GatewayError,
#     SignatureVerificationError,
#     ServerError,
# )

# from django.conf import settings

# TOKEN_VALIDITY_MINUTES = 10
# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def get_token():
#     try:
#         token_obj = APIToken.objects.latest('created_at')
#         print("Existing token found:", token_obj.token)
#         if timezone.now() < token_obj.created_at + timedelta(minutes=TOKEN_VALIDITY_MINUTES):
#             return token_obj
#         else:
#             print("Token expired, refreshing...")
#             status_code, new_token = auth_api()
#             if status_code == 200 and new_token:
#                 token_obj = APIToken.objects.create(token=new_token)
#                 print("New token obtained:", token_obj.token)
#                 return token_obj
#             else:
#                 # print("Failed to refresh token")
#                 return render(request, 'app_shop/token_error.html', {'error': auth_res.get('error')})
#     except APIToken.DoesNotExist:
#         print("No existing token, obtaining new one...")
#         status_code, new_token = auth_api()
#         if status_code == 200 and new_token:
#             token_obj = APIToken.objects.create(token=new_token)
#             print("New token obtained:", token_obj.token)
#             return token_obj
#         else:
#             # print("Failed to obtain initial token")
#             return render(request, 'app_shop/token_error.html', {'error': auth_res.get('error')})

# def make_post(endpoint, payload, fetchId=None, fetchVal=None):
#     base_url = ExternalAPI.EXTERNAL_APIS['BASE_URL']
#     ep = ExternalAPI.EXTERNAL_APIS[endpoint]
#     url = f"{base_url}{ep}"
#     token = get_token().token
#     print("Making POST request to:", ep)
#     headers = {
#             'Accept': 'application/json',
#             'Cookie': f'sessionId={token}',
#             'Content-Type': 'application/json',
#             }
#     if fetchId is not None and fetchId == "mobile":
#         headers['mobileNumber'] = fetchVal
#     elif fetchId is not None and fetchId == "customerRefNo":
#         headers['customerRefNo'] = fetchVal
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         return_value = {
#             "status": response.status_code,
#             "code": None,
#             "data": None,
#             "reason": None
#         }
#         # paste the print block here to debug response
#         try:
#             content = response.json()
#         except ValueError:
#             content = response.text.strip()
#         # ---- SUCCESS HANDLING ----
#         if response.ok:  # 200–299
#             if isinstance(content, (dict, list)):
#                 # JSON success response
#                 return_value["code"] = "Success"
#                 return_value["data"] = content
#             elif isinstance(content, str):
#                 # Plain text success like "Data Validated"
#                 return_value["code"] = "Success"
#                 return_value["data"] = {"message": content}
#             else:
#                 return_value["code"] = "Success"
#                 return_value["data"] = {"raw": str(content)}
#          # ---- ERROR HANDLING ----
#         else:
#             if isinstance(content, dict):
#                 # Error codes like {"code": 39, "reason": "..."}
#                 return_value["code"] = str(content.get("code", "Error"))
#                 return_value["reason"] = content.get("reason") or str(content)
#             else:
#                 return_value["code"] = "Error"
#                 return_value["reason"] = str(content)
#         return return_value

#     except requests.RequestException as e:
#         return {
#             "status": None,
#             "code": "RequestFailed",
#             "data": None,
#             "reason": str(e)
#         }

# def auth_api():

#     partner_id = settings.PARTNER_ID
#     username = settings.USR_ID
#     password = settings.PASSWORD
#     url = settings.BASE_URL + ExternalAPI.EXTERNAL_APIS['AUTH_ENDPOINT']
    
#     credentials = f'{username}:{password}'
#     encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
#     auth_header = f'Basic {encoded_credentials}'

#     headers = {
#         'partner_id': partner_id,
#         'Accept': 'application/json',
#         'Authorization': auth_header,
#         }

#     response = requests.post(url, headers=headers)

#     data = json.loads(response.text)  # Converts JSON string → dict
#     token = data.get('sessionId')

#     # print("Status Code:", response.status_code)
#     # print("Response Body:", token)
#     return response.status_code, token

# def generate_transaction_ref(csRefNo, session):
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     return f"TRX-{csRefNo}-{session}-{timestamp}"

# def create_razorpay_order(amount, currency='INR'):
#     try:
#         data = {
#             'amount': amount,  # Razorpay expects amount in paise
#             'currency': currency,
#             'payment_capture': '1'  # Auto-capture payment after successful authorization
#         }
#         order = client.order.create(data=data)
#         return order['id']
#     except (BadRequestError, GatewayError, SignatureVerificationError, ServerError) as e:
#         print("Razorpay Error:", e)
#         return None

import json
import base64
import requests
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import APIToken
from .api_config import ExternalAPI
from requests.exceptions import RequestException
from app_shop.models import Balance
import razorpay
from razorpay.errors import (
    BadRequestError,
    GatewayError,
    SignatureVerificationError,
    ServerError,
)
from decimal import Decimal

logger = logging.getLogger(__name__)

TOKEN_VALIDITY_MINUTES = 10
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# -------------------
# Auth helpers
# -------------------
def auth_api():
    """
    Calls the external auth endpoint and returns (status_code, token_str_or_None)
    """
    partner_id = settings.PARTNER_ID
    username = settings.USR_ID
    password = settings.PASSWORD
    url = settings.BASE_URL + ExternalAPI.EXTERNAL_APIS.get('AUTH_ENDPOINT', '')

    credentials = f'{username}:{password}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    auth_header = f'Basic {encoded_credentials}'

    headers = {
        'partner_id': partner_id,
        'Accept': 'application/json',
        'Authorization': auth_header,
    }

    try:
        response = requests.post(url, headers=headers, timeout=8)
        try:
            data = response.json()
        except ValueError:
            data = {}
        token = data.get('sessionId') or data.get('session_id') or data.get('token')
        return response.status_code, token
    except RequestException as e:
        logger.exception("Auth request failed")
        return None, None

def generate_transaction_ref(customer_ref_no, session_key):
    """
    Create a unique transaction reference using customer ref no,
    session key, and timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TRX-{customer_ref_no}-{session_key}-{timestamp}"

def get_token():
    """
    Returns token string on success, or None on failure.
    Stores token string in APIToken model (latest row).
    """
    try:
        token_obj = APIToken.objects.latest('created_at')
        if timezone.now() < token_obj.created_at + timedelta(minutes=TOKEN_VALIDITY_MINUTES):
            return token_obj.token
        else:
            status_code, new_token = auth_api()
            if status_code == 200 and new_token:
                token_obj = APIToken.objects.create(token=new_token)
                return token_obj.token
            else:
                logger.warning("Failed to refresh token")
                return None
    except APIToken.DoesNotExist:
        status_code, new_token = auth_api()
        if status_code == 200 and new_token:
            token_obj = APIToken.objects.create(token=new_token)
            return token_obj.token
        else:
            logger.warning("Failed to obtain initial token")
            return None

# -------------------
# Generic request helper (POST)
# Flexible: supports callers using keyword token=... or default token via get_token()
# -------------------
def make_post(endpoint=None, payload=None, fetchId=None, fetchVal=None, token=None, **kwargs):
    """
    endpoint: key name in ExternalAPI.EXTERNAL_APIS (e.g. 'GOLD_PRICE_ENDPOINT')
    payload: dict payload to POST (json)
    fetchId / fetchVal: optional additional header values (mobile/customerRefNo)
    token: optional, if provided it will be used as session token; otherwise get_token() is used

    Returns normalized dict: {"status": int|None, "code": str|None, "data": dict|list|str|None, "reason": str|None}
    """
    # Allow callers who pass endpoint as kwarg in other order
    if not endpoint:
        return {"status": None, "code": "MissingEndpoint", "data": None, "reason": "No endpoint specified"}

    base_url = ExternalAPI.EXTERNAL_APIS.get('BASE_URL') or settings.BASE_URL
    ep = ExternalAPI.EXTERNAL_APIS.get(endpoint)
    if not ep:
        # endpoint not found
        return {"status": None, "code": "EndpointMissing", "data": None, "reason": f"Endpoint key {endpoint} not found"}

    url = f"{base_url}{ep}"

    # Get token if not explicitly supplied
    if not token:
        token = get_token()

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    if token:
        headers['Cookie'] = f'sessionId={token}'

    if fetchId is not None and fetchVal is not None:
        if fetchId == "mobile":
            headers['mobileNumber'] = str(fetchVal)
        elif fetchId == "customerRefNo":
            headers['customerRefNo'] = str(fetchVal)
        else:
            # allow arbitrary header key
            headers[fetchId] = str(fetchVal)

    try:
        response = requests.post(url, json=payload or {}, headers=headers, timeout=10)
        return_value = {
            "status": response.status_code if response is not None else None,
            "code": None,
            "data": None,
            "reason": None
        }

        # Attempt to parse JSON, fallback to text
        try:
            content = response.json()
        except ValueError:
            content = response.text.strip() if response.text else None

        if response.ok:
            # Success path
            if isinstance(content, (dict, list)):
                return_value["code"] = "Success"
                return_value["data"] = content
            elif isinstance(content, str):
                return_value["code"] = "Success"
                return_value["data"] = {"message": content}
            else:
                return_value["code"] = "Success"
                return_value["data"] = {"raw": str(content)}
        else:
            # Error path
            if isinstance(content, dict):
                return_value["code"] = str(content.get("code", "Error"))
                return_value["reason"] = content.get("reason") or json.dumps(content)
            else:
                return_value["code"] = "Error"
                return_value["reason"] = str(content)
        return return_value

    except RequestException as e:
        logger.exception("RequestException making POST to %s", url)
        return {
            "status": None,
            "code": "RequestFailed",
            "data": None,
            "reason": str(e)
        }
    except Exception as e:
        logger.exception("Unexpected error making POST")
        return {
            "status": None,
            "code": "UnexpectedError",
            "data": None,
            "reason": str(e)
        }

# -------------------
# Razorpay helper
# -------------------
def create_razorpay_order(amount, currency='INR'):
    try:
        data = {
            'amount': amount,  # amount in paise
            'currency': currency,
            'payment_capture': '1'
        }
        order = client.order.create(data=data)
        return order.get('id')
    except (BadRequestError, GatewayError, SignatureVerificationError, ServerError) as e:
        logger.exception("Razorpay error")
        return None

# -------------------
# Metal price helpers
# -------------------

def get_user_holdings(custRefNo):
    """
    Returns total, blocked and available quantities for gold and silver.
    """

    gold = Balance.objects.filter(custRefNo=custRefNo, currency_pair="XAU/INR").first()
    silver = Balance.objects.filter(custRefNo=custRefNo, currency_pair="XAG/INR").first()

    return {
        "gold_total": gold.bal_quantity if gold else Decimal("0"),
        "gold_blocked": gold.blocked_quantity if gold else Decimal("0"),
        "gold_available": (gold.bal_quantity - gold.blocked_quantity) if gold else Decimal("0"),

        "silver_total": silver.bal_quantity if silver else Decimal("0"),
        "silver_blocked": silver.blocked_quantity if silver else Decimal("0"),
        "silver_available": (silver.bal_quantity - silver.blocked_quantity) if silver else Decimal("0"),
    }


def deduct_from_balance(custRefNo, currency_pair, qty):
    """
    Deduct sold qty from user's balance after SELL is fully captured.
    Prevents negative values.
    """
    bal = Balance.objects.filter(custRefNo=custRefNo, currency_pair=currency_pair).first()
    if not bal:
        return False

    bal.bal_quantity -= qty
    if bal.bal_quantity < 0:
        bal.bal_quantity = 0

    bal.save(update_fields=["bal_quantity"])
    return True

def _extract_price(obj):
    """
    Try many common shapes and return float price or None.
    """
    if obj is None:
        return None
    # If top-level is dict, check common keys
    if isinstance(obj, dict):
        for k in ('buy_pretax', 'buyPrice', 'price', 'last_price', 'lastPrice', 'rate', 'value', 'close'):
            if k in obj and obj[k] is not None:
                try:
                    return float(obj[k])
                except (TypeError, ValueError):
                    pass
        # check nested containers
        for kk in ('result', 'data', 'payload', 'response'):
            if kk in obj and isinstance(obj[kk], (dict, list)):
                p = _extract_price(obj[kk])
                if p is not None:
                    return p
        # arrays inside dict
        for kk in ('series', 'prices', 'dataPoints', 'candles'):
            if kk in obj and isinstance(obj[kk], (list, tuple)) and len(obj[kk]) > 0:
                return _extract_price(obj[kk][-1])
    # If list/tuple -> try last (most recent)
    if isinstance(obj, (list, tuple)) and len(obj) > 0:
        return _extract_price(obj[-1])
    # If it's a plain number or numeric string
    try:
        return float(obj)
    except (TypeError, ValueError):
        return None

# def get_metal_price(metal, timeframe="1D"):
#     """
#     Generic metal price getter using the external endpoints.
#     metal: 'gold' or 'silver' (case-insensitive)
#     Returns float price or None. Also returns raw data for debugging if needed.
#     """
#     metal_name = metal.lower()
#     # Mapping: choose endpoint keys used in your ExternalAPI.EXTERNAL_APIS
#     if metal_name in ('gold', 'xau'):
#         ep_key = 'GOLD_PRICE_ENDPOINT'
#     elif metal_name in ('silver', 'xag'):
#         ep_key = 'SILVER_PRICE_ENDPOINT'
#     else:
#         # fallback, try a generic price endpoint if available
#         ep_key = 'PRICE_ENDPOINT'

#     payload = {"timeFrame": timeframe}
#     res = make_post(ep_key, payload)
#     price = None
#     raw = None
#     if res and isinstance(res, dict) and res.get('status') and 200 <= res['status'] < 300:
#         raw = res.get('data')
#         price = _extract_price(raw)

#     else:
#         # if res exists but no status, still try if data present
#         if res and isinstance(res, dict):
#             raw = res.get('data')
#             price = _extract_price(raw)
#     return price, raw

def get_metal_price(metal, timeframe="1D"):
    """
    Fetches metal price and safely extracts buy_pretax or similar fields.
    Works for your real API format:
        [{'buy_pretax': 12326.32, 'date_time': '20251210'}]
    """
    metal_name = metal.lower()

    if metal_name in ("gold", "xau"):
        ep_key = "GOLD_PRICE_ENDPOINT"
    elif metal_name in ("silver", "xag"):
        ep_key = "SILVER_PRICE_ENDPOINT"
    else:
        ep_key = "PRICE_ENDPOINT"

    response = make_post(ep_key, {"timeFrame": timeframe})

    price = None
    raw = None

    # Case 1 — API returns list directly (YOUR API)
    if isinstance(response, list):
        raw = response
        price = _extract_price(raw)

    # Case 2 — API returns { "data": [ ... ] }
    elif isinstance(response, dict):
        raw = response.get("data") or response
        price = _extract_price(raw)

    # Convert to float safely
    try:
        price = float(price) if price is not None else None
    except:
        price = None

    return price, raw


def get_gold_price(timeframe="1D"):
    return get_metal_price('gold', timeframe)

def get_silver_price(timeframe="1D"):
    return get_metal_price('silver', timeframe)



# print("###############################################################")
# print("Request URL:", url)
# print("###############################################################")
# print("Request Headers:", headers)
# print("###############################################################")
# print("Request Payload:", payload)
# print("###############################################################")
# print("Status Code:", response.status_code)
# print("###############################################################")
# print("Response recieved:", response)
# print("###############################################################")
# print("Response Content-Type:", response.headers['Content-Type'])
# print(response.text) 
# print("###############################################################")