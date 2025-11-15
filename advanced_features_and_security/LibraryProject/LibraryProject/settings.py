"""
Django settings for LibraryProject with comprehensive HTTPS and security configurations.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Always set to False in production

ALLOWED_HOSTS = [
    'yourdomain.com', 
    'www.yourdomain.com',
    'localhost', 
    '127.0.0.1',
    '0.0.0.0'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bookshelf',  # Your custom app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom security middleware
    'LibraryProject.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'LibraryProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'LibraryProject.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Enhanced security: minimum 8 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'bookshelf.CustomUser'

# ==================== HTTPS & SECURITY CONFIGURATION ====================
# Comprehensive security settings for production deployment

# HTTPS Configuration - Critical for secure data transmission
SECURE_SSL_REDIRECT = True  # ✅ Redirect all HTTP requests to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Required when behind a proxy

# HTTP Strict Transport Security (HSTS) - Protects against SSL stripping attacks
SECURE_HSTS_SECONDS = 31536000  # ✅ 1 year - Instruct browsers to only use HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # ✅ Apply HSTS to all subdomains
SECURE_HSTS_PRELOAD = True  # ✅ Allow preloading in browser HSTS lists

# Secure Cookies - Prevent cookie theft via man-in-the-middle attacks
SESSION_COOKIE_SECURE = True  # ✅ Session cookies only sent over HTTPS
CSRF_COOKIE_SECURE = True  # ✅ CSRF cookies only sent over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent client-side script access to session cookie
CSRF_COOKIE_HTTPONLY = True  # Additional protection for CSRF cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection for cross-site requests
CSRF_COOKIE_SAMESITE = 'Lax'

# Security Headers - Protection against various web vulnerabilities
X_FRAME_OPTIONS = 'DENY'  # ✅ Prevent clickjacking by denying framing
SECURE_CONTENT_TYPE_NOSNIFF = True  # ✅ Prevent MIME type sniffing
SECURE_BROWSER_XSS_FILTER = True  # ✅ Enable browser XSS filtering

# Additional Security Headers (implemented via custom middleware)
SECURE_REFERRER_POLICY = 'same-origin'  # Control referrer information

# Content Security Policy (via custom middleware)
CSP_DIRECTIVES = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
    'script-src': ["'self'"],
    'img-src': ["'self'", "data:", "https:"],
    'font-src': ["'self'", "https://cdnjs.cloudflare.com"],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
}

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
    'https://*.yourdomain.com'
]

# Session Security
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on each request

# File Upload Security
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB max upload size
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644  # Secure file permissions

# Email Configuration (for production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Logging Configuration for Security Monitoring
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'bookshelf': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security-specific logger
SECURITY_LOGGER = 'bookshelf.security'

# Production-specific settings
if DEBUG:
    # Development overrides
    ALLOWED_HOSTS = ['*']
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
