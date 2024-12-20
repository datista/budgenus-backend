from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from core.api.views import TenantViewSet, DomainViewSet, InvitationViewSet
from budgenus.admin import admin_site  # Import our custom admin site

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'invitations', InvitationViewSet, basename='invitation')

# Tenant-specific URLs
urlpatterns = [
    # Admin interface for tenant schema
    path('admin/', admin_site.urls),  # Use our custom admin site

    # Tenant-specific API endpoints
    path('api/', include([
        path('users/', include('users.api.urls')),  # User management within tenant
        path('core/', include(router.urls)),    # Core functionality
    ])),
    
    # DRF browsable API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Debug toolbar in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns