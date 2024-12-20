from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import utils as django_db_utils
from users.models import Address
from .serializers import (
    UserSerializer, UserDetailSerializer, AddressSerializer,
    CustomTokenObtainPairSerializer, RegisterSerializer
)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AuthViewSet(viewsets.GenericViewSet):
    """
    Authentication endpoints for public schema
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def get_serializer_class(self):
        if self.action == 'login':
            return CustomTokenObtainPairSerializer
        return RegisterSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        view = CustomTokenObtainPairView.as_view()
        return view(request._request)

    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"[DEBUG] {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PublicUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API endpoint for users (read-only)
    Used in public schema for user registration and profile viewing
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only allow users to view their own profile in public schema
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

class TenantUserViewSet(viewsets.ModelViewSet):
    """
    Tenant-specific API endpoint for users
    Used within tenant schema for user management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        # In tenant context, users can only see users within their tenant
        return User.objects.filter(tenant=self.request.tenant)

class AddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for addresses (tenant-specific)
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter addresses to return only those belonging to the current tenant
        return Address.objects.filter(user__tenant=self.request.tenant)
