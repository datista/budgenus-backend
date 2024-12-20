from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, tenant=None, **extra_fields):
        """
        Create and save a user with the given email, password, and tenant.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
            
        # Check if tenant is required (for non-superuser accounts)
        is_superuser = extra_fields.get('is_superuser', False)
        if not tenant and not is_superuser:
            raise ValueError(_('A tenant is required for non-superuser accounts'))
            
        email = self.normalize_email(email)
        user = self.model(email=email, tenant=tenant, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, tenant=None, **extra_fields):
        """
        Create and save a SuperUser with the given email, password, and tenant.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        # Tenant is optional for superusers
        return self.create_user(email, password, tenant, **extra_fields)