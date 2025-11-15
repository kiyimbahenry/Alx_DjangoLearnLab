"""
Django settings for LibraryProject with enhanced security configurations.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Set to False in production

ALLOWED_HOSTS = ['yourdomain.com', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bookshelf',  # Your custom app
    # 'csp',  # REMOVED - Content Security Policy
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'csp.middleware.CSPMiddleware',  # REMOVED
    'LibraryProject.middleware.CSPMiddleware',  # ADDED - Our custom CSP middleware
]

# ... [Keep all your existing settings until SECURITY SETTINGS] ...

# ==================== SECURITY SETTINGS ====================

# Security middleware settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Cookie security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# HTTPS settings (uncomment in production with SSL)
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Content Security Policy (CSP) settings - Manual implementation
CSP_DIRECTIVES = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
    'script-src': ["'self'"],
    'img-src': ["'self'", "data:", "https:"],
    'font-src': ["'self'", "https://cdnjs.cloudflare.com"],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"],
}

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com', 'https://*.yourdomain.com']

# Session security
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
