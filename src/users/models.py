from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .managers import CustomUserManager
from django.db import transaction
from tenants.models import Tenant

class Address(models.Model):
    country = models.CharField(_('country'), max_length=100)
    state = models.CharField(_('state/province'), max_length=100)
    city = models.CharField(_('city'), max_length=100)
    address_line1 = models.CharField(_('address line 1'), max_length=100)
    address_line2 = models.CharField(_('address line 2'), max_length=100, blank=True)
    zip_code = models.CharField(_('ZIP/Postal code'), max_length=20)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other'))
    ]

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=50)
    last_name = models.CharField(_('last name'), max_length=50)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    gender = models.CharField(
        _('gender'), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        null=True,
        blank=True
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.PROTECT,
        null=True,  
        blank=True,  
        related_name='users',
        help_text=_('The tenant (organization) this user belongs to. A user can only belong to one tenant.')
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=2,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def create_with_tenant(self, tenant_name=None):
        """Create a tenant for the user and associate them."""
        print(f"[DEBUG] Starting create_with_tenant for user: {self.email}")

        # Guard: Skip if user already has a tenant or is superuser
        if self.tenant or self.is_superuser:
            print(f"[DEBUG] User already has tenant or is superuser")
            return self

        try:
            with transaction.atomic():
                # Ensure user has primary key
                if not self.pk:
                    print(f"[DEBUG] Saving user first")
                    self.save()

                # Generate tenant name if not provided
                tenant_name = tenant_name or f"{self.first_name}'s Tenant"
                print(f"[DEBUG] Using tenant name: {tenant_name}")

                # Create tenant
                try:
                    tenant = Tenant.create_for_user(self, tenant_name)
                    print(f"[DEBUG] Tenant created successfully: {tenant.schema_name}")
                except Exception as tenant_error:
                    print(f"[DEBUG] Failed to create tenant: {str(tenant_error)}")
                    
                    # Guard: Handle duplicate tenant name
                    if "duplicate key value violates unique constraint" in str(tenant_error):
                        raise Exception("A tenant with this name already exists. Please choose a different organization name.")
                    raise tenant_error

                # Associate tenant with user
                print(f"[DEBUG] Updating user with tenant")
                self.tenant = tenant
                self.save()
                print(f"[DEBUG] User saved successfully with tenant")
                
                return self

        except Exception as e:
            print(f"[DEBUG] Error in create_with_tenant: {str(e)}")
            # Guard: Clean up user if creation fails
            if self.pk:
                print(f"[DEBUG] Deleting user due to error")
                self.delete()
            raise Exception(f"Failed to create user and tenant: {str(e)}")

    @property
    def full_address(self):
        """Return the full address as a formatted string"""
        if hasattr(self, 'address'):
            address = self.address
            address_parts = []
            if address.address_line1:
                address_parts.append(address.address_line1)
            if address.address_line2:
                address_parts.append(address.address_line2)
            if address.city:
                address_parts.append(address.city)
            if address.state:
                address_parts.append(address.state)
            if address.country:
                address_parts.append(address.country)
            if address.zip_code:
                address_parts.append(address.zip_code)
            return ', '.join(filter(None, address_parts))
        return None

@receiver(post_delete, sender=CustomUser)
def delete_orphan_address(sender, instance, **kwargs):
    """Delete address if no other users are using it"""
    if instance.address:
        if not instance.address.users.exists():
            instance.address.delete()