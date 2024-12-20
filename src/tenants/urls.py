from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet)
router.register(r'domains', views.DomainViewSet)
router.register(r'invitations', views.InvitationViewSet, basename='invitation')

app_name = 'tenants'

urlpatterns = [
    path('api/', include(router.urls)),
]
