from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import uuid

# Create your models here.

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
    email = models.EmailField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['email']

    def __str__(self):
        return f"Invitation for {self.email}"

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
