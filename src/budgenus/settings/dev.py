# src/budgenus/settings/dev.py
from .base import *

# Security settings for development
DEBUG = True
SECRET_KEY = 'dev-secret-key'  # Only for development
ALLOWED_HOSTS = ['*']  # Allow all hosts in development

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Print emails to console

# Add development-specific settings
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Get base settings
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Add session auth for development
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Add browsable API for development
    ],
}

# Development-specific middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Add debug_toolbar to SHARED_APPS
SHARED_APPS += ['debug_toolbar']

# Recalculate INSTALLED_APPS with debug_toolbar
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Debug toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# Static Files - development configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Tenant Domain
DOMAIN = 'localhost'