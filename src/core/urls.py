from django.urls import path, include

# All core endpoints are now in the API
urlpatterns = [
    path('api/v1/', include('core.api.urls')),
]