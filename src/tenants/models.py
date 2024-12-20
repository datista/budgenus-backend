from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
import re

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_owned',
        null=True,
        blank=True,
        help_text='The user who created and owns this tenant. They have admin privileges.'
    )
    auto_create_schema = True

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """Check if tenant subscription is active"""
        if self.paid_until:
            return timezone.now().date() <= self.paid_until
        return self.is_on_trial

    @property
    def is_on_trial(self):
        """Check if tenant is currently on trial"""
        if not self.trial_end_date:
            return False
        return timezone.now().date() <= self.trial_end_date

    def start_trial(self, days=30):
        """Start trial period for tenant"""
        self.trial_end_date = timezone.now().date() + timedelta(days=days)
        self.save()

    @classmethod
    def create_for_user(cls, user, tenant_name=None):
        """Create a tenant and domain for a user."""
        try:
            print(f"[DEBUG] Starting create_for_user with tenant_name: {tenant_name}")
            
            # Generate tenant name if not provided
            if not tenant_name:
                tenant_name = f"{user.first_name}'s workspace" if user.first_name else f"{user.email.split('@')[0]}'s workspace"
            print(f"[DEBUG] Using tenant name: {tenant_name}")
            
            # Generate and clean schema name
            schema_name = cls.generate_schema_name(tenant_name)
            print(f"[DEBUG] Generated schema name: {schema_name}")
            
            # Check if schema name already exists
            if cls.objects.filter(schema_name=schema_name).exists():
                raise Exception("A tenant with this name already exists. Please choose a different organization name.")
            
            # Create tenant
            tenant = cls.objects.create(
                name=tenant_name,
                schema_name=schema_name,
                owner=user
            )
            print(f"[DEBUG] Tenant created successfully")
            
            # Create domain
            domain_name = f"{schema_name}.{settings.DOMAIN}"
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=True
            )
            print(f"[DEBUG] Domain created successfully: {domain_name}")
            
            return tenant
        except Exception as e:
            print(f"[DEBUG] Error in create_for_user: {str(e)}")
            raise

    @classmethod
    def generate_schema_name(cls, tenant_name):
        # Sanitize schema name
        schema_name = re.sub(r'[^a-zA-Z0-9]', '_', tenant_name.lower())[:50]
        return schema_name

class Domain(DomainMixin):
    """
    Domain model for tenant.
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='tenant_domains'
    )

class Invitation(models.Model):
    """
    Model for tenant invitations
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        EXPIRED = 'expired', 'Expired'
        DECLINED = 'declined', 'Declined'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tenant_invitations_sent'
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['tenant', 'email']

    def __str__(self):
        return f"Invitation for {self.email} to {self.tenant.name}"

    @property
    def is_expired(self):
        """Check if invitation has expired"""
        return timezone.now() > self.expires_at

    def accept(self):
        """Accept invitation"""
        if self.is_expired:
            raise ValueError("Invitation has expired")
        if self.status != self.Status.PENDING:
            raise ValueError("Invitation is not pending")
        
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save()

    def decline(self):
        """Decline invitation"""
        if self.status != self.Status.PENDING:
            raise ValueError("Invitation is not pending")
        
        self.status = self.Status.DECLINED
        self.save()

    def save(self, *args, **kwargs):
        """Set expiry date on creation"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
