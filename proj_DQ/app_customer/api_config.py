# services/api_config.py

class ExternalAPI:
    # BASE_URL = 'https://cemuat.mmtcpamp.com'
    SESSION_COOKIE_NAME = 'sessionId'
    EXTERNAL_APIS = {
        'BASE_URL': 'https://cemuat.mmtcpamp.com',
        'AUTH_ENDPOINT': '/security/login',
        'CREATE_PROFILE_ENDPOINT': '/customer/createProfile',
        'UPDATE_PROFILE_ENDPOINT': '/customer/updateProfile',
        'PORTFOLIO_ENDPOINT': '/customer/getPortfolio',
        'GET_PROFILE_ENDPOINT': '/oat/getProfile',
        'GOLD_PRICE_ENDPOINT': '/XAU/INR',
        'GOLD_PRICE_ENDPOINT': '/XAG/INR',
        }
