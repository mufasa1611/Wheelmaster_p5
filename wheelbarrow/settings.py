import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env_path = os.path.join(BASE_DIR, '.env')
print(f"\nLoading environment from: {env_path}")
load_dotenv(env_path, override=True)  

# Debug Configuration
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Database Configuration
DB_STATUS = os.getenv('DB_STATUS', '').strip().lower()
print(f"Raw DB_STATUS from env: '{os.getenv('DB_STATUS')}'")
print(f"Processed DB_STATUS: '{DB_STATUS}'")

DATABASE_URL = None

# Determine which database to use
if DB_STATUS == 'remote':
    DATABASE_URL = os.getenv('DATABASE_URL_REMOTE')
    print(f"Using REMOTE database at: {DATABASE_URL}")
elif DB_STATUS == 'local':
    DATABASE_URL = os.getenv('DATABASE_URL_LOCAL')
    print(f"Using LOCAL database at: {DATABASE_URL}")
else:
    print(f"Warning: Invalid DB_STATUS '{DB_STATUS}'. Must be 'local' or 'remote'.")
    print("Defaulting to LOCAL database.")
    DATABASE_URL = os.getenv('DATABASE_URL_LOCAL')

if not DATABASE_URL:
    raise ValueError("No database URL configured! Check your .env file.")

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=9000,  # Keep connection alive for 15 minutes
    )
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# Backup Directory (only in development)
if DEBUG:
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '127.0.0.1:5500',
    '8000-mufasa1611-wheelmasterp-g2n0827wbqv.ws.codeinstitute-ide.net',
    'wheelmaster-fd0d6b0f7d27.herokuapp.com',
    'testserver',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'home',
    'products',
    'bag',
    'checkout',
    'profiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_countries',
]

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'wheelbarrow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
             os.path.join(BASE_DIR, 'templates'),
             os.path.join(BASE_DIR, 'templates', 'allauth'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'bag.contexts.bag_contents',
            ],
            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field',
            ],
        },
    },
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'wheel-master.alhanein.net' 
EMAIL_PORT = 587
EMAIL_USE_TLS = True  
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL') 

WSGI_APPLICATION = 'wheelbarrow.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# Authentication settings
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Wheelmaster - '
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'  # Change to https in production
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_PRESERVE_USERNAME_CASING = False  # Converts to lowercase
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'administrator', 'superuser']
ACCOUNT_SESSION_REMEMBER = None  # Let the users choose with remember me checkbox
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# Additional allauth security settings
ACCOUNT_RATE_LIMITS = {
    "login": "10/m",          # 10 successful logins per minute
    "login_failed": "5/m",    # 5 failed attempts per minute
    "signup": "5/m",          # 5 signups per minute
    "send_mail": "5/m",       # 5 emails per minute
    "reset_password": "5/m"   # 5 password reset attempts per minute
}
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_ON_GET = False  # Require POST request to logout
ACCOUNT_MAX_EMAIL_ADDRESSES = 1  # Limit number of email addresses per user
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 10  # 10 days in seconds
SESSION_COOKIE_SECURE = False  
CSRF_COOKIE_SECURE = False    
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't expire when browser closes if remember me is checked

# Session security settings
SESSION_SECURITY_EXPIRE_AFTER = 60 * 30  # 30 minutes of inactivity
SESSION_SECURITY_WARN_AFTER = 60 * 25    # Warn after 25 minutes

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', default='')
STRIPE_WH_SECRET = os.getenv('STRIPE_WH_SECRET', default='')

FREE_DELIVERY_THRESHOLD = 100
STANDARD_DELIVERY_PERCENTAGE = 10

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',  
    },
}