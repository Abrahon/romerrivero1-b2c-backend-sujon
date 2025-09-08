
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url 

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

    "cloudinary",
    "cloudinary_storage",

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
    'b2b.profiles',
    'b2b.contact',

]
ASGI_APPLICATION = "romerrivero1.asgi.application"   

SITE_ID = 1

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Database settings (POSTGRES)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
        
        
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        # Replace this value with your local database's connection string.
        default='postgresql://romero_user:Bg52tJ3BJ3Yh2Nwt2gmfpkJvgqKq6L7x@dpg-d2tmeu8gjchc73a0o8bg-a.oregon-postgres.render.com/romero',
        conn_max_age=600
    )
}

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
ADMIN_EMAIL = os.getenv('EMAIL_HOST_USER')

# Database settings (SQLite)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3', 
#         'NAME': BASE_DIR / 'db.sqlite3',  
#     }
# }

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
AUTH_USER_MODEL = 'accounts_b.B2BUser' 
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
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
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
