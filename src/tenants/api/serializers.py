from rest_framework import serializers
from django.utils.text import slugify
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from tenants.models import Tenant, Domain, Invitation

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['domain', 'is_primary', 'tenant']
        read_only_fields = ['tenant']

class TenantSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, read_only=True)
    is_on_trial = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    trial_days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'schema_name', 'name', 'paid_until', 
            'trial_end_date', 'is_on_trial', 'is_active',
            'trial_days_remaining', 'domains', 'created_at'
        ]
        read_only_fields = ['schema_name', 'trial_end_date']

    def get_trial_days_remaining(self, obj):
        """Calculate remaining trial days"""
        if not obj.trial_end_date:
            return 0
        remaining = (obj.trial_end_date - timezone.now().date()).days
        return max(0, remaining)

    def create(self, validated_data):
        """Create a new tenant with a primary domain"""
        # Generate a unique schema name
        base_schema = slugify(validated_data['name'])[:40]
        schema_name = base_schema
        
        # Ensure schema name is unique
        counter = 1
        while Tenant.objects.filter(schema_name=schema_name).exists():
            schema_name = f"{base_schema}-{counter}"
            counter += 1
        
        validated_data['schema_name'] = schema_name
        tenant = Tenant.objects.create(**validated_data)
        tenant.start_trial()
        return tenant

class InvitationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            'id', 'tenant', 'tenant_name', 'email', 
            'invited_by_name', 'status', 'created_at',
            'expires_at', 'days_until_expiry'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'expires_at']

    def get_days_until_expiry(self, obj):
        """Calculate days until invitation expires"""
        if not obj.expires_at:
            return 0
        remaining = (obj.expires_at - timezone.now()).days
        return max(0, remaining)

    def create(self, validated_data):
        """Create a new invitation and send email"""
        invitation = Invitation.objects.create(**validated_data)
        self._send_invitation_email(invitation)
        return invitation

    def _send_invitation_email(self, invitation):
        """Send invitation email to user"""
        accept_url = reverse('accept-invitation', kwargs={'token': invitation.token})
        accept_url = f"{settings.FRONTEND_URL}{accept_url}"
        
        subject = f"Invitation to join {invitation.tenant.name}"
        message = f"""
        Hello,

        You have been invited to join {invitation.tenant.name} by {invitation.invited_by.get_full_name()}.
        
        To accept this invitation, please click the following link:
        {accept_url}
        
        This invitation will expire in {invitation.days_until_expiry} days.
        
        Best regards,
        The Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
            fail_silently=False,
        )
