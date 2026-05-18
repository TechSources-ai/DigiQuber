# from pathlib import Path
# import os
# import dj_database_url
# import environ

# DJANGO_ENV = os.getenv('DJANGO_ENV', 'local')

# if DJANGO_ENV == 'production':
#     from proj_DG.ssm_config import SSM
# else:
#     env = environ.Env()
#     environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env.staging'))
#     SSM = {
#         'app_secret_key': env('app_secret_key'),
#         'partner_id': env('partner_id'),
#         'usr_id': env('usr_id'),
#         'password': env('password'),
#         'base_url': env('base_url'),
#         'RAZORPAY_KEY_ID': env('RAZORPAY_KEY_ID'),
#         'RAZORPAY_KEY_SECRET': env('RAZORPAY_KEY_SECRET'),
#         'AZURE_EMAIL_CONNECTION': env('AZURE_EMAIL_CONNECTION_STRING'),
#         'AZURE_EMAIL_SENDER': env('AZURE_EMAIL_SENDER'),
#         'FRONTEND_URL': env('FRONTEND_URL'),
#         'provider_session_id': env('provider_session_id'),
#         'DATABASE_URL': env('DATABASE_URL'),
#         'AWS_STORAGE_BUCKET_NAME': env('AWS_STORAGE_BUCKET_NAME'),
#         'AWS_S3_REGION_NAME': env('AWS_S3_REGION_NAME'),
#         'CLOUDFRONT_DOMAIN': env('CLOUDFRONT_DOMAIN'),
#     }

# BASE_DIR = Path(__file__).resolve().parent.parent

# # --------------------------------------------------
# # SECRETS FROM SSM
# # --------------------------------------------------
# SECRET_KEY = SSM['app_secret_key']

# PARTNER_ID = SSM['partner_id']
# USR_ID = SSM['usr_id']
# PASSWORD = SSM['password']
# BASE_URL = SSM['base_url']
# RAZORPAY_KEY_ID = SSM['RAZORPAY_KEY_ID']
# RAZORPAY_KEY_SECRET = SSM['RAZORPAY_KEY_SECRET']
# AZURE_EMAIL_CONNECTION_STRING = SSM['AZURE_EMAIL_CONNECTION']
# AZURE_EMAIL_SENDER = SSM['AZURE_EMAIL_SENDER']
# FRONTEND_URL = SSM['FRONTEND_URL']
# PROVIDER_SESSION_ID = SSM['provider_session_id']
# AWS_STORAGE_BUCKET_NAME = SSM['AWS_STORAGE_BUCKET_NAME']
# AWS_S3_REGION_NAME = SSM['AWS_S3_REGION_NAME']
# CLOUDFRONT_DOMAIN = SSM['CLOUDFRONT_DOMAIN']

# # --------------------------------------------------
# # CORE SETTINGS
# # --------------------------------------------------
# DEBUG = DJANGO_ENV != 'production'

# ALLOWED_HOSTS = [
#     '16.112.118.116',
#     "13.203.209.236",
#     "localhost",
#     "127.0.0.1",
#     '98.91.239.3',
#     'digitalquber.com',
#     'www.digitalquber.com',
# ]

# CSRF_TRUSTED_ORIGINS = [
#     "http://13.203.209.236:8080",
#     "https://digitalquber.com",
#     "https://www.digitalquber.com",
# ]

# # --------------------------------------------------
# # SECURITY HEADERS
# # --------------------------------------------------
# X_FRAME_OPTIONS = 'DENY'
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

# if DJANGO_ENV == 'production':
#     SECURE_HSTS_SECONDS = 31536000
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SESSION_COOKIE_HTTPONLY = True    # ← add
#     CSRF_COOKIE_HTTPONLY = True       # ← add
#     SESSION_COOKIE_SAMESITE = 'Lax'  # ← add
#     CSRF_COOKIE_SAMESITE = 'Lax'     # ← add
# else:
#     SECURE_SSL_REDIRECT = False
#     SESSION_COOKIE_SECURE = False
#     CSRF_COOKIE_SECURE = False
#     SESSION_COOKIE_HTTPONLY = True    # ← add (safe even on HTTP/local)
#     CSRF_COOKIE_HTTPONLY = True       # ← add
#     SESSION_COOKIE_SAMESITE = 'Lax'  # ← add
#     CSRF_COOKIE_SAMESITE = 'Lax'     # ← add

# # --------------------------------------------------
# # APPLICATION
# # --------------------------------------------------
# AUTH_USER_MODEL = 'app_login.CustomUser'

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'app_admin',
#     'app_login',
#     'app_user',
#     'app_shop',
#     'app_trade',
#     'app_sell',
#     'app_pay',
#     'storages',
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'csp.middleware.CSPMiddleware', 
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'proj_DG.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': ['templates'],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'proj_DG.wsgi.application'

# # --------------------------------------------------
# # DATABASE
# # --------------------------------------------------
# DATABASES = {
#     'default': dj_database_url.parse(SSM['DATABASE_URL'])
# }

# # --------------------------------------------------
# # PASSWORD VALIDATION
# # --------------------------------------------------
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# # --------------------------------------------------
# # INTERNATIONALISATION
# # --------------------------------------------------
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# # --------------------------------------------------
# # EMAIL
# # --------------------------------------------------
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# # --------------------------------------------------
# # AUTH
# # --------------------------------------------------
# LOGIN_URL = 'signin'
# LOGIN_REDIRECT_URL = '/post-login-handler/'
# LOGOUT_REDIRECT_URL = 'home'

# # --------------------------------------------------
# # AWS / S3 / CLOUDFRONT
# # --------------------------------------------------
# if DJANGO_ENV == 'production':
#     AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN
#     AWS_LOCATION = 'static'

#     STORAGES = {
#         "staticfiles": {
#             "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
#         },
#         "default": {
#             "BACKEND": "django.core.files.storage.FileSystemStorage",
#         },
#     }

#     STATIC_URL = f'https://{CLOUDFRONT_DOMAIN}/static/'

# else:
#     STATIC_URL = '/static/'
#     STATICFILES_DIRS = [BASE_DIR / "static"]
#     STATIC_ROOT = BASE_DIR / "staticfiles"

# # --------------------------------------------------
# # MISC
# # --------------------------------------------------
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from pathlib import Path
import os
import dj_database_url
import environ

DJANGO_ENV = os.getenv('DJANGO_ENV', 'local')

if DJANGO_ENV == 'production':
    from proj_DG.ssm_config import SSM
else:
    env = environ.Env()
    environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env.staging'))
    SSM = {
        'app_secret_key': env('app_secret_key'),
        'partner_id': env('partner_id'),
        'usr_id': env('usr_id'),
        'password': env('password'),
        'base_url': env('base_url'),
        'RAZORPAY_KEY_ID': env('RAZORPAY_KEY_ID'),
        'RAZORPAY_KEY_SECRET': env('RAZORPAY_KEY_SECRET'),
        'AZURE_EMAIL_CONNECTION': env('AZURE_EMAIL_CONNECTION_STRING'),
        'AZURE_EMAIL_SENDER': env('AZURE_EMAIL_SENDER'),
        'FRONTEND_URL': env('FRONTEND_URL'),
        'provider_session_id': env('provider_session_id'),
        'DATABASE_URL': env('DATABASE_URL'),
        'AWS_STORAGE_BUCKET_NAME': env('AWS_STORAGE_BUCKET_NAME'),
        'AWS_S3_REGION_NAME': env('AWS_S3_REGION_NAME'),
        'CLOUDFRONT_DOMAIN': env('CLOUDFRONT_DOMAIN'),
    }

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECRETS FROM SSM
# --------------------------------------------------
SECRET_KEY = SSM['app_secret_key']

PARTNER_ID = SSM['partner_id']
USR_ID = SSM['usr_id']
PASSWORD = SSM['password']
BASE_URL = SSM['base_url']
RAZORPAY_KEY_ID = SSM['RAZORPAY_KEY_ID']
RAZORPAY_KEY_SECRET = SSM['RAZORPAY_KEY_SECRET']
AZURE_EMAIL_CONNECTION_STRING = SSM['AZURE_EMAIL_CONNECTION']
AZURE_EMAIL_SENDER = SSM['AZURE_EMAIL_SENDER']
FRONTEND_URL = SSM['FRONTEND_URL']
PROVIDER_SESSION_ID = SSM['provider_session_id']
AWS_STORAGE_BUCKET_NAME = SSM['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = SSM['AWS_S3_REGION_NAME']
CLOUDFRONT_DOMAIN = SSM['CLOUDFRONT_DOMAIN']

# --------------------------------------------------
# CORE SETTINGS
# --------------------------------------------------
DEBUG = DJANGO_ENV != 'production'

ALLOWED_HOSTS = [
    '16.112.118.116',
    "13.203.209.236",
    "localhost",
    "127.0.0.1",
    '98.91.239.3',
    'digitalquber.com',
    'www.digitalquber.com',
]

CSRF_TRUSTED_ORIGINS = [
    "http://13.203.209.236:8080",
    "https://digitalquber.com",
    "https://www.digitalquber.com",
]

# --------------------------------------------------
# SECURITY HEADERS
# --------------------------------------------------
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

if DJANGO_ENV == 'production':
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

# --------------------------------------------------
# CONTENT SECURITY POLICY
# --------------------------------------------------
CSP_DEFAULT_SRC = ("'self'",)

CSP_SCRIPT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
    "https://checkout.razorpay.com",
    "https://cdn.jsdelivr.net/npm/apexcharts",
)

CSP_STYLE_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
)

CSP_FONT_SRC = (
    "'self'",
    "https://cdn.jsdelivr.net",
)

CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://via.placeholder.com",
)

CSP_CONNECT_SRC = (
    "'self'",
    "https://checkout.razorpay.com",
    "https://cemuat.mmtcpamp.com",
)

CSP_FRAME_SRC = (
    "https://api.razorpay.com",
    "https://checkout.razorpay.com",
)

# Report-only in staging/local so nothing breaks,
# enforced automatically in production
CSP_REPORT_ONLY = DJANGO_ENV != 'production'

# --------------------------------------------------
# APPLICATION
# --------------------------------------------------
AUTH_USER_MODEL = 'app_login.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_admin',
    'app_login',
    'app_user',
    'app_shop',
    'app_trade',
    'app_sell',
    'app_pay',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proj_DG.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'proj_DG.wsgi.application'

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASES = {
    'default': dj_database_url.parse(SSM['DATABASE_URL'])
}
DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# INTERNATIONALISATION
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# EMAIL
# --------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# --------------------------------------------------
# AUTH
# --------------------------------------------------
LOGIN_URL = 'signin'
LOGIN_REDIRECT_URL = '/post-login-handler/'
LOGOUT_REDIRECT_URL = 'home'

# --------------------------------------------------
# AWS / S3 / CLOUDFRONT
# --------------------------------------------------
if DJANGO_ENV == 'production':
    AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN
    AWS_LOCATION = 'static'

    STORAGES = {
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        },
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }

    STATIC_URL = f'https://{CLOUDFRONT_DOMAIN}/static/'

else:
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------
# MISC
# --------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/app.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/errors.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 3,
            'level': 'ERROR',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'app_shop': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'app_pay': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'app_trade': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'app_sell': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'app_login': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}