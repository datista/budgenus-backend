from django.utils.translation import gettext_lazy as _
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security settings
SECRET_KEY = 'your-secret-key-here'  # Better to use environment variable
DEBUG = False  # Set True in dev.py
ALLOWED_HOSTS = []

# Tenant Apps Configuration
# Apps available in public schema and all tenants
SHARED_APPS = [
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # tenant support
    'django_tenants',  # mandatory
    'tenants',       # tenant management
    'core',          # core functionality
    
    # your shared apps
    'users',         # custom user model
    
    # third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
]

# Apps available only in tenant schemas
TENANT_APPS = [
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # your tenant-specific apps
    'users',
    'tenants',
    'core',
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Internationalization settings
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
]

USE_I18N = True  # Enables Django's translation system
USE_L10N = True  # Enables localization of data formatting
USE_TZ = True    # Enables timezone support
TIME_ZONE = 'UTC'  # UTC is recommended for storing times

# URL Configuration
ROOT_URLCONF = 'budgenus.urls'  # Main URLs configuration
PUBLIC_SCHEMA_URLCONF = 'budgenus.urls_public'  # Public tenant URLs

# Translations
LOCALE_PATHS = [BASE_DIR / 'locale']

# Middleware - Order is important
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.LanguageMiddleware',  # Language handling
    'core.middleware.AdminAccessMiddleware',  # Admin access control
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database Configuration - Consider moving to dev.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'budgenus-postgres',
        'USER': 'budgenus',
        'PASSWORD': 'budgenus',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Tenant Configuration
TENANT_MODEL = "tenants.Tenant"  # Model for tenant
TENANT_DOMAIN_MODEL = "tenants.Domain"  # Model for tenant domains
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True   # Tell Django to use public schema if no tenant is found
PUBLIC_SCHEMA_NAME = 'public'
FORCE_SCRIPT_NAME = None
APPEND_SLASH = True

# Database Routing
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Authentication Configuration
AUTH_USER_MODEL = 'users.CustomUser'
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

# Static Files Configuration
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Short-lived for security
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Longer-lived for convenience
    'ROTATE_REFRESH_TOKENS': True,                  # Enhanced security
    'BLACKLIST_AFTER_ROTATION': True,               # Prevent token reuse
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

# Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Budgenus API',
    'DESCRIPTION': 'API documentation for Budgenus application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True