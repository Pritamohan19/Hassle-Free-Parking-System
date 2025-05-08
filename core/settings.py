import os
from pathlib import Path

# ========================
# Base Directory
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# Secret Key
# ========================
SECRET_KEY = 'django-insecure-r6#)0mgct_=&dul2-shj@7++%(p-!)^%t=p9+^^499__vlhoqn'

# ========================
# Debug Mode
# ========================
DEBUG = True

# ========================
# Allowed Hosts
# ========================
ALLOWED_HOSTS = []

# ========================
# Installed Apps
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parking',  # Your app
]

# ========================
# Middleware
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================
# Root URL Configuration
# ========================
ROOT_URLCONF = 'core.urls'

# ========================
# Templates Configuration
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Look here for templates like parking-login.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ========================
# WSGI Application
# ========================
WSGI_APPLICATION = 'core.wsgi.application'

# ========================
# Database
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========================
# Password Validators
# ========================
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

# ========================
# Internationalization
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========================
# Static Files
# ========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ========================
# Media Files (Optional)
# ========================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========================
# Custom User Model
# ========================
AUTH_USER_MODEL = 'parking.User'

# ========================
# Redirect URLs
# ========================
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# ========================
# Booking Settings
# ========================
BOOKING_MIN_LEAD_TIME_HOURS = 2

# ========================
# Email Backend (For Development)
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ========================
# Default Auto Field
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Add these settings to your Django settings.py file

# Razorpay Settings
RAZORPAY_KEY_ID = "rzp_test_3BW2YFJNQS5PYu"
RAZORPAY_KEY_SECRET = "ukRTpeikvVZAU5kSdFtncyTE"
# For production, use environment variables instead
# import os
# RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
# RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')