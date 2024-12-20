from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from tenants.models import Tenant, Domain, Invitation
from .serializers import TenantSerializer, DomainSerializer, InvitationSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

class IsSuperUser(permissions.BasePermission):
    """Only allow superusers to access tenant management"""
    def has_permission(self, request, view):
        return request.user.is_superuser

class TenantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tenants
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

class DomainViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tenant domains
    """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def perform_create(self, serializer):
        """Ensure domain is associated with a tenant"""
        tenant_id = self.request.data.get('tenant')
        tenant = get_object_or_404(Tenant, id=tenant_id)
        serializer.save(tenant=tenant)

class InvitationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tenant invitations
    """
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter invitations based on user role"""
        if self.request.user.is_superuser:
            return Invitation.objects.all()
        return Invitation.objects.filter(tenant__owner=self.request.user)

    def perform_create(self, serializer):
        """Create invitation with current user as inviter"""
        serializer.save(invited_by=self.request.user)

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend invitation email"""
        invitation = self.get_object()
        
        # Check if invitation is still valid
        if invitation.is_expired:
            return Response({
                'error': 'Invitation has expired'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if invitation.status != Invitation.Status.PENDING:
            return Response({
                'error': 'Invitation has already been used'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset expiry and resend email
        invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
        invitation.save()
        
        serializer = self.get_serializer(invitation)
        serializer._send_invitation_email(invitation)
        
        return Response({
            'message': 'Invitation resent successfully'
        })
