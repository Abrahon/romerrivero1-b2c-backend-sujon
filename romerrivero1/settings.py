# from pathlib import Path
# import os
# from datetime import timedelta
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(os.path.join(BASE_DIR, '.env'))

# # SECURITY SETTINGS
# DEBUG = os.getenv('DEBUG', 'True') == 'True'  
# SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key') 
# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# # APPLICATION DEFINITION
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'corsheaders',
#     'rest_framework',
#     'rest_framework_simplejwt',
#     'rest_framework.authtoken',
#     'django.contrib.sites',
#     'allauth',
#     'allauth.account',
#     'allauth.socialaccount',
#     'allauth.socialaccount.providers.google',  
#     'allauth.socialaccount.providers.facebook',  
#     'allauth.socialaccount.providers.twitter',
#     'drf_yasg',
#     "channels",
#     "notifications",
#     'accounts',
#     'common',
#     'support',
#     'b2c.products',
#     'b2c.reviews',
#     'b2c.user_profile',
#     'b2c.cart',
#     'b2c.checkout',
#     'b2c.chat',
#     'b2c.admin.admin_profile',
#     'b2c.admin.coupons',
#     'b2c.orders.apps.OrdersConfig',  
#     'b2c.payments.apps.PaymentsConfig',
#     'b2c.admin.add_product.apps.AddProductConfig',
#     'b2b.product',
#     'b2b.inquiries',
#     'b2b.connections',
#     'b2b.order',
# ]

# ASGI_APPLICATION = "romerrivero1.asgi.application"

# SITE_ID = 1

# # CHANNEL LAYERS (For Real-time features like WebSockets)
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)], 
#         },
#     },
# }

# MIDDLEWARE = [
#     "corsheaders.middleware.CorsMiddleware",
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'allauth.account.middleware.AccountMiddleware',
# ]
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # CORS SETTINGS
# CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')

# # STRIPE SETTINGS (For Payment Gateway)
# STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
# STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
# STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# # EMAIL SETTINGS (For notifications, order confirmations, etc.)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# # DATABASE SETTINGS (SQLite for now, but can be switched to PostgreSQL in production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',  # SQLite setup
#     }
# }
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     ],
#     "DEFAULT_PERMISSION_CLASSES": [
#         "rest_framework.permissions.IsAuthenticated",  # 👈 Default
#     ],
# }

# # STATIC AND MEDIA FILE SETTINGS
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# # TEMPLATE SETTINGS
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],  # Add custom templates if any
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

# # AUTHENTICATION SETTINGS
# AUTH_USER_MODEL = 'accounts.User'  # Use custom user model if defined
# AUTHENTICATION_BACKENDS = (
#     'allauth.account.auth_backends.AuthenticationBackend',
#     'django.contrib.auth.backends.ModelBackend',
# )

# # SOCIAL AUTH SETTINGS (Google/Facebook login)
# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_KEY')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET')

# # JWT SETTINGS
# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
# }

# # REST_FRAMEWORK SETTINGS (Django REST Framework)
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
# }

# # SESSION AND CSRF SETTINGS (For production)
# if not DEBUG:
#     CSRF_COOKIE_SECURE = True
#     SESSION_COOKIE_SECURE = True
#     SECURE_SSL_REDIRECT = True
#     X_FRAME_OPTIONS = 'DENY'

# # Development settings (allowing all origins for CORS)
# if DEBUG:
#     CORS_ALLOW_ALL_ORIGINS = True

# # ALLOWED HOSTS for deployment
# ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'b2b-b2c-romerrivero1.onrender.com']

# # LOGIN AND LOGOUT URL CONFIGURATIONS
# LOGIN_URL = 'accounts_login'
# LOGOUT_URL = 'account_logout'
# LOGIN_REDIRECT_URL = 'dashboard'
# LOGOUT_REDIRECT_URL = 'userlogin'

# # SECURITY SETTINGS
# if not DEBUG:
#     CSRF_COOKIE_SECURE = True
#     SESSION_COOKIE_SECURE = True
#     SECURE_SSL_REDIRECT = True
#     X_FRAME_OPTIONS = 'DENY'

# # Custom development settings for local
# if DEBUG:
#     CORS_ALLOW_ALL_ORIGINS = True

# # Allowed Hosts (use for production environments)
# ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'b2b-b2c-romerrivero1.onrender.com']


#  # In your settings.py
# ROOT_URLCONF = 'romerrivero1.urls'


from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Security settings
DEBUG = os.getenv('DEBUG', 'True') == 'True'  
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key') 
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  
    'allauth.socialaccount.providers.facebook',  
    'allauth.socialaccount.providers.twitter', 
    
    'drf_yasg',
    "channels",
    "notifications",
    'accounts',
    'common',
    'support',
    'b2c.products',
    'b2c.reviews',
    'b2c.user_profile',
    'b2c.cart',
    'b2c.checkout',
    # 'b2c.orders',
    'b2c.chat',
    'b2c.admin.admin_profile',
    # 'b2c.admin.add_product',
    'b2c.admin.coupons',
    'b2c.orders.apps.OrdersConfig',  
    'b2c.payments.apps.PaymentsConfig',
    'b2c.admin.add_product.apps.AddProductConfig',

    # b2b
    'b2b.product',
    'b2b.accounts_b',
    'b2b.inquiries',
    'b2b.connections',
    'b2b.order',
    'b2b.customer',
    'b2b.analytics',
    
     
    
    

]
ASGI_APPLICATION = "romerrivero1.asgi.application"   

SITE_ID = 1


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],   
        },
    },
}

# session for reset password 
SESSION_COOKIE_AGE = 600  
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  

import os

ALLOWED_HOSTS = ["*"] 

# If using static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    
    'allauth.account.middleware.AccountMiddleware',  
]

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')

# Stripe settings
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Database settings (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': BASE_DIR / 'db.sqlite3',  
    }
}

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Authentication settings
AUTH_USER_MODEL = 'accounts.User' 
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '649570633464-7p40grhfbe7o5347oq2244tvjr0kiv9v.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'


ACCOUNT_SIGNUP_FIELDS = [ 'email*', 'password1*', 'password2*']
# ACCOUNT_LOGIN_METHODS = ['email*', 'password1*']




# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  
ACCOUNT_AUTHENTICATED_REDIRECT_URL = '/'  
ACCOUNT_LOGOUT_ON_GET = True 

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
      'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  
}



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=60),
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    X_FRAME_OPTIONS = 'DENY'

# Custom settings for development
if DEBUG:
    # To be used for running the development server only
    CORS_ALLOW_ALL_ORIGINS = True
    
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'b2b-b2c-romerrivero1.onrender.com']

 # In your settings.py
ROOT_URLCONF = 'romerrivero1.urls'

# Login and Logout URL Configurations
LOGIN_URL = 'accounts_login'  
LOGOUT_URL = 'account_logout'  
LOGIN_REDIRECT_URL = 'dashboard'  
LOGOUT_REDIRECT_URL = 'userlogin'  

