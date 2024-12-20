# src/budgenus/urls_public.py
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from budgenus.admin import admin_site  # Import our custom admin site

# Public URLs (non-tenant specific)
urlpatterns = [
    # Admin interface
    path('admin/', admin_site.urls),  # Use our custom admin site
    
    # Public API endpoints
    path('api/auth/', include('users.api.urls')),  # Authentication endpoints
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # DRF browsable API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Debug toolbar in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns