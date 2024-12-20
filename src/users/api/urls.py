from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from . import views

# Create two different routers for public and tenant URLs
public_router = DefaultRouter()
tenant_router = DefaultRouter()

# Public routes (available in public schema)
public_router.register(r'users', views.PublicUserViewSet, basename='public-user')

# Tenant routes (available in tenant schemas)
tenant_router.register(r'users', views.TenantUserViewSet, basename='tenant-user')
tenant_router.register(r'addresses', views.AddressViewSet, basename='address')

app_name = 'users-api'

# Public URLs - used in urls_public.py
auth_urlpatterns = [
    # Authentication endpoints
    path('register/', views.AuthViewSet.as_view({'post': 'register', 'get': 'register'}), name='register'),
    path('login/', views.AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', views.AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Public user management URLs
public_urlpatterns = [
    path('', include(public_router.urls)),
]

# Tenant URLs - used in urls_tenant.py
tenant_urlpatterns = [
    path('', include(tenant_router.urls)),
]

# Default urlpatterns - for backward compatibility
urlpatterns = auth_urlpatterns + public_urlpatterns
