from rest_framework import serializers
from django.utils.text import slugify
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from core.models import Invitation

class InvitationSerializer(serializers.ModelSerializer):
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 
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
        invitation = Invitation.objects.create(
            email=validated_data['email'],
            invited_by=self.context['request'].user
        )
        self._send_invitation_email(invitation)
        return invitation

    def _send_invitation_email(self, invitation):
        """Send invitation email to user"""
        accept_url = reverse('invitation-accept', kwargs={'pk': invitation.id})
        full_url = f"{settings.FRONTEND_URL}{accept_url}"
        
        subject = f'Invitation'
        message = f'''
        You have been invited by {invitation.invited_by.get_full_name()}.
        
        Click the following link to accept the invitation:
        {full_url}
        
        This invitation will expire on {invitation.expires_at}.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
            fail_silently=False,
        )
