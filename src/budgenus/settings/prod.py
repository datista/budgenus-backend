from .base import *
import os

# SECURITY WARNING: Keep production environment variables secure
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Security settings
DEBUG = False
ALLOWED_HOSTS = [
   'your-domain.com',
   'www.your-domain.com',
   'api.your-domain.com',
]

# Production security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Database Configuration
DATABASES = {
   'default': {
       'ENGINE': 'django_tenants.postgresql_backend',
       'NAME': os.environ.get('DB_NAME'),
       'USER': os.environ.get('DB_USER'),
       'PASSWORD': os.environ.get('DB_PASSWORD'),
       'HOST': os.environ.get('DB_HOST'),
       'PORT': os.environ.get('DB_PORT', '5432'),
       'CONN_MAX_AGE': 60,  # 1 minute connection persistence
   }
}

# Cache Configuration (using Redis)
CACHES = {
   'default': {
       'BACKEND': 'django_redis.cache.RedisCache',
       'LOCATION': os.environ.get('REDIS_URL'),
       'OPTIONS': {
           'CLIENT_CLASS': 'django_redis.client.DefaultClient',
       }
   }
}

# Email Configuration (using SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@your-domain.com'

# Static/Media Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Use the base REST_FRAMEWORK settings which are already production-ready
# You can override specific settings if needed
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Get base settings
    # Add any production-specific overrides here
}

# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    # Add your frontend domains here
    "https://your-frontend-domain.com",
    'https://your-domain.com',
    'https://www.your-domain.com',
]
CORS_ALLOW_CREDENTIALS = True

# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Session Settings
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# Other Production Settings
PREPEND_WWW = True  # Redirect example.com to www.example.com
ADMINS = [('Your Name', 'your.email@your-domain.com')]
MANAGERS = ADMINS

# Tenant Domain
DOMAIN = 'budgenus.com'

""" Key features of this production settings file:

Environment variables for sensitive data
Enhanced security settings
Production-grade database settings
Caching configuration
Email setup
Static/Media files handling
CORS security
Comprehensive logging
Session management
Server security headers

Remember to:

Never commit sensitive values to version control
Use environment variables
Keep your secret key secure
Regularly update security settings
Monitor logs
Set up proper backups

Would you like me to:

Explain any specific section in detail?
Show how to set up the environment variables?
Add more security configurations?
 CopyRetryClaude does not have the ability to run the code it generates yet. """