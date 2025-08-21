from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# SECURITY SETTINGS
DEBUG = os.getenv('DEBUG', 'True') == 'True'  
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key') 
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# APPLICATION DEFINITION
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
    'b2c.chat',
    'b2c.admin.admin_profile',
    'b2c.admin.coupons',
    'b2c.orders.apps.OrdersConfig',  
    'b2c.payments.apps.PaymentsConfig',
    'b2c.admin.add_product.apps.AddProductConfig',
    'b2b.product',
    # 'b2b.inquiries',
    'b2b.connections',
    'b2b.order',
]

ASGI_APPLICATION = "romerrivero1.asgi.application"

SITE_ID = 1

# CHANNEL LAYERS (For Real-time features like WebSockets)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)], 
        },
    },
}

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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS SETTINGS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')

# STRIPE SETTINGS (For Payment Gateway)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# EMAIL SETTINGS (For notifications, order confirmations, etc.)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# DATABASE SETTINGS (SQLite for now, but can be switched to PostgreSQL in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite setup
    }
}

# STATIC AND MEDIA FILE SETTINGS
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# TEMPLATE SETTINGS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add custom templates if any
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

# AUTHENTICATION SETTINGS
AUTH_USER_MODEL = 'accounts.User'  # Use custom user model if defined
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# SOCIAL AUTH SETTINGS (Google/Facebook login)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET')

# JWT SETTINGS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

# REST_FRAMEWORK SETTINGS (Django REST Framework)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# SESSION AND CSRF SETTINGS (For production)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    X_FRAME_OPTIONS = 'DENY'

# Development settings (allowing all origins for CORS)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# ALLOWED HOSTS for deployment
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'b2b-b2c-romerrivero1.onrender.com']

# LOGIN AND LOGOUT URL CONFIGURATIONS
LOGIN_URL = 'accounts_login'
LOGOUT_URL = 'account_logout'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'userlogin'

# SECURITY SETTINGS
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    X_FRAME_OPTIONS = 'DENY'

# Custom development settings for local
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# Allowed Hosts (use for production environments)
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', 'b2b-b2c-romerrivero1.onrender.com']


 # In your settings.py
ROOT_URLCONF = 'romerrivero1.urls'

