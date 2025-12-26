import requests
from django.conf import settings

def provider_login():
    """
    Uses Basic Auth (username + password) and partner_id header
    to get sessionId from MMTC-PAMP.
    """
    url = f"{settings.BASE_URL}/security/login"

    headers = {
        "partner_id": settings.PARTNER_ID,
        "Accept": "application/json",
    }

    auth = (settings.USR_ID, settings.PASSWORD)  # Basic Auth

    resp = requests.post(url, headers=headers, auth=auth)
    resp.raise_for_status()

    data = resp.json()
    return data.get("sessionId"), data
