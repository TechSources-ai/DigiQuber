import requests
from .api_config import ExternalAPI
from django.conf import settings
import base64
from requests.exceptions import RequestException

sessionId = '123'

def make_post(endpoint, payload):
    url = f"{EXTERNAL_APIS['BASE_URL']}{EXTERNAL_APIS[endpoint]}"
    headers = {
        'Accept': 'application/json',
        'Cookie': f'sessionId={sessionId}',
        'Content-Type': 'application/json',
        }
    try:
        response = requests.post(url, json=payload, headers=headers)
        # Handle response
        if response.status_code == 200:
            data = response.json()  # Or response.text, depending on API
            print("Status Code:", response.status_code)
            print("Response Body:", response.text)
            return response.text
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def auth_api():

    partner_id = settings.PARTNER_ID
    username = settings.USR_ID
    password = settings.PASSWORD
    url = settings.BASE_URL + ExternalAPI.EXTERNAL_APIS['AUTH_ENDPOINT']
    
    credentials = f'{username}:{password}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    auth_header = f'Basic {encoded_credentials}'

    headers = {
        'partner_id': partner_id,
        'Accept': 'application/json',
        'Authorization': auth_header,
        }

    response = requests.post(url, headers=headers)
    # print("Status Code:", response.status_code)
    # print("Response Body:", response.text)
    return response.status_code, response.text