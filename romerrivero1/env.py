import os
import environ
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.abspath('.')


env = environ.Env(
    DATABASE_URL=(str, f'sqlite:///{BASE_DIR}/db.sqlite3'),
)



DEBUG = env('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY')


CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS



# PROD_ENV_DISABLE_SWAGGER = env.bool('PROD_ENV_DISABLE_SWAGGER', default=False)
# PROD_ENV_DISABLE_ADMIN = env.bool('PROD_ENV_DISABLE_ADMIN', default=False)
# DEV_TEST_SHOW_ALL_REGISTERED_MODELS = env.bool('DEV_TEST_SHOW_ALL_REGISTERED_MODELS', default=False)
# DEV_TEST_MULTIPARTPARSER_ONLY = env.bool('DEV_TEST_MULTIPARTPARSER_ONLY', default=False)



# SWAGGER_DEFAULT_API_URL = env('SWAGGER_DEFAULT_API_URL', default='http://127.0.0.1:8000')
PROJECT_NAME = env('PROJECT_NAME', default='Django Project')
PROJECT_DESCRIPTION = env('PROJECT_DESCRIPTION', default=PROJECT_NAME)
PROJECT_VERSION = env('PROJECT_VERSION', default='v1')


EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=None)



DB = env.db('DATABASE_URL')
