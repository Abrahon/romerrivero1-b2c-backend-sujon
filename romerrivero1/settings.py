
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url 
from decouple import config
import dj_database_url
import os


# Load environment variables from the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os  .path.join(BASE_DIR, '.env'))

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
    # new added for jwt token blacklisting
    # 'rest_framework',
    # 'rest_framework_simplejwt.token_blacklist',

    "cloudinary",
    "cloudinary_storage",

    'drf_yasg',
    "channels",
    "notifications",
    'accounts',
    'common',
    # 'promotions',
    'support',
    'b2c.products',
    'b2c.reviews',
    'b2c.user_profile',
    'b2c.cart',
    'b2c.checkout',
    'b2c.coupons',
    'b2c.wishlist',
    'b2c.promotions',
    # 'b2c.orders',
    'b2c.chat',
    'b2c.admin.admin_profile',
    'dashboard',
    'visitors',
    'b2c.customers',
   
    'b2c.orders.apps.OrdersConfig',  
    'b2c.payments.apps.PaymentsConfig',


]
ASGI_APPLICATION = "romerrivero1.asgi.application"   

SITE_ID = 1

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"



# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv(
#             'DATABASE_URL',
#             'postgresql://romero_user:Bg52tJ3BJ3Yh2Nwt2gmfpkJvgqKq6L7x@dpg-d2tmeu8gjchc73a0o8bg-a.oregon-postgres.render.com/romero'
#         ),
#         conn_max_age=600,
#         ssl_require=True  
#     )
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}





CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

FRONTEND_REDIRECT_URL = "https://gamerbytes.us/google/callback"
# session for reset password 
SESSION_COOKIE_AGE = 600  
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  


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
    'visitors.middleware.VisitorTrackingMiddleware',
    
      
]

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://10.10.13.15:3000',).split(',')

# Stripe settings
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 465     
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'no-reply@gamerbytes.us'
EMAIL_HOST_PASSWORD = 'Ayon28@gmail.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

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
# AUTH_USER_MODEL = 'accounts_b.B2BUser' 


AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

# google 
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '649570633464-7p40grhfbe7o5347oq2244tvjr0kiv9v.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'
SOCIALACCOUNT_PROVIDERS  = {
    'google':{
        'APP':{
            'cliendt_id': '',
            'secret': '',

        }
    }
}




ACCOUNT_SIGNUP_FIELDS = [ 'email*', 'password1*', 'password2*']




# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  
ACCOUNT_AUTHENTICATED_REDIRECT_URL = '/'  
ACCOUNT_LOGOUT_ON_GET = True 

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
      'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  

     'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
    "ROTATE_REFRESH_TOKENS": True,                   # issue new refresh token each time
    "BLACKLIST_AFTER_ROTATION": True, 
    # "AUTH_HEADER_TYPES": ("Bearer",),
}


FRONTEND_REDIRECT_URL = "https://gamerbytes.us/google/callback"
SESSION_COOKIE_AGE = 600  
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  


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
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "dashboard" 
ACCOUNT_LOGOUT_REDIRECT_URL = "login"

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI")
FRONTEND_REDIRECT_URL = config("FRONTEND_REDIRECT_URL")