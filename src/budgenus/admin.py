from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from tenants.models import Tenant, Domain, Invitation
from users.models import CustomUser

# Create a custom admin site
class BudgenusAdminSite(admin.AdminSite):
    site_header = 'Budgenus Administration'
    site_title = 'Budgenus Admin'
    index_title = 'Administration'

# Instantiate the custom admin site
admin_site = BudgenusAdminSite(name='budgenus_admin')

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1
    readonly_fields = ['tenant_admin_link']

    def tenant_admin_link(self, obj):
        if obj and obj.is_primary:
            url = f"http://{obj.domain}/admin/"
            return format_html('<a href="{}" target="_blank">Access Tenant Admin</a>', url)
        return "Not a primary domain"

class UserInline(admin.TabularInline):
    model = CustomUser
    extra = 0
    readonly_fields = ['email', 'full_name', 'phone_number']
    fields = ['email', 'full_name', 'phone_number']
    can_delete = False
    max_num = 0
    verbose_name = "Member"
    verbose_name_plural = "Members"

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def phone_number(self, obj):
        return obj.phone_number or "-"

    def has_add_permission(self, request, obj=None):
        return False

class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0
    readonly_fields = ['email', 'invited_by', 'status', 'created_at', 'expires_at']
    fields = ['email', 'invited_by', 'status', 'created_at', 'expires_at']
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at', 'paid_until', 'is_active', 'is_on_trial', 'tenant_admin_link', 'member_count']
    list_filter = ['created_at', 'paid_until', 'trial_end_date']
    search_fields = ['name', 'owner__email', 'users__email']
    readonly_fields = ['created_at', 'tenant_admin_link', 'schema_name', 'member_count', 'is_active', 'is_on_trial']
    inlines = [DomainInline, UserInline, InvitationInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'schema_name')
        }),
        ('Subscription Details', {
            'fields': ('paid_until', 'trial_end_date')
        }),
        ('Status', {
            'fields': ('is_active', 'is_on_trial')
        }),
        ('Admin Access', {
            'fields': ('tenant_admin_link',)
        }),
        ('Statistics', {
            'fields': ('member_count', 'created_at')
        })
    )

    def member_count(self, obj):
        return obj.users.count()
    member_count.short_description = "Total Members"

    def tenant_admin_link(self, obj):
        if obj.tenant_domains.filter(is_primary=True).exists():
            domain = obj.tenant_domains.filter(is_primary=True).first()
            url = f"http://{domain.domain}/admin/"
            return format_html('<a href="{}" target="_blank">Access Tenant Admin</a>', url)
        return "No primary domain set"
    tenant_admin_link.short_description = "Tenant Admin"

    def delete_queryset(self, request, queryset):
        """Handle bulk deletions"""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete tenants")
        
        with transaction.atomic():
            for tenant in queryset:
                try:
                    # First, delete all invitations
                    invitations = tenant.tenant_invitations.all()
                    if invitations.exists():
                        invitations.delete()
                    print(f"[DEBUG] Deleting (set) tenants: {queryset}")
                    # Delete all domains
                    tenant.tenant_domains.all().delete()
                    
                    # Delete all associated users
                    users = tenant.users.all()
                    if users.exists():
                        users.delete()
                    
                    # Finally delete the tenant
                    tenant.delete()
                    
                    messages.success(request, f"Successfully deleted tenant: {tenant.name} and all its users")
                except Exception as e:
                    messages.error(request, f"Error deleting tenant {tenant.name}: {str(e)}")
                    continue

    def delete_model(self, request, obj):
        """Handle single tenant deletion"""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete tenants")
        
        with transaction.atomic():
            try:
                # First, delete all invitations
                invitations = obj.tenant_invitations.all()
                if invitations.exists():
                    invitations.delete()
                
                # Delete all domains
                obj.tenant_domains.all().delete()
                
                # Delete all associated users
                users = obj.users.all()
                if users.exists():
                    users.delete()
                
                # Finally delete the tenant
                obj.delete()
                
                messages.success(request, f"Successfully deleted tenant: {obj.name} and all its users")
            except Exception as e:
                messages.error(request, f"Error deleting tenant: {str(e)}")
                raise

class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary', 'tenant_admin_link']
    list_filter = ['is_primary', 'tenant']
    search_fields = ['domain', 'tenant__name']
    readonly_fields = ['tenant_admin_link']

    def tenant_admin_link(self, obj):
        if obj.is_primary:
            url = f"http://{obj.domain}/admin/"
            return format_html('<a href="{}" target="_blank">Access Tenant Admin</a>', url)
        return "Not a primary domain"
    tenant_admin_link.short_description = "Tenant Admin"

class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'invited_by', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['email', 'tenant__name', 'invited_by__email']
    readonly_fields = ['created_at', 'expires_at']

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'tenant', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Access', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'tenant')
        }),
        ('Important dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )

    def delete_queryset(self, request, queryset):
        """Handle bulk user deletions"""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete users")
        
        with transaction.atomic():
            for user in queryset:
                try:
                    # Check if user owns any tenants
                    owned_tenants = Tenant.objects.filter(owner=user)
                    if owned_tenants.exists():
                        messages.warning(request, f"User {user.email} is an owner of {owned_tenants.count()} tenant(s). Please reassign ownership first.")
                        continue

                    # Get user's tenant before deletion
                    tenant = user.tenant

                    # Remove user from any groups
                    user.groups.clear()
                    
                    # Remove user permissions
                    user.user_permissions.clear()
                    
                    # Delete any invitations created by this user
                    Invitation.objects.filter(invited_by=user).delete()
                    
                    # Delete the user
                    user.delete()
                    
                    # If tenant exists and this was the last user, delete the tenant
                    if tenant and not tenant.users.exists():
                        # Delete all tenant's invitations
                        tenant.invitations.all().delete()
                        # Delete all tenant's domains
                        tenant.tenant_domains.all().delete()
                        # Delete the tenant
                        tenant.delete()
                        messages.success(request, f"Deleted user {user.email} and their tenant {tenant.name} (last user)")
                    else:
                        messages.success(request, f"Successfully deleted user: {user.email}")
                except Exception as e:
                    messages.error(request, f"Error deleting user {user.email}: {str(e)}")
                    continue

    def delete_model(self, request, obj):
        """Handle single user deletion"""
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete users")
        
        with transaction.atomic():
            try:
                # Check if user owns any tenants
                owned_tenants = Tenant.objects.filter(owner=obj)
                if owned_tenants.exists():
                    messages.error(request, f"Cannot delete user {obj.email} as they own {owned_tenants.count()} tenant(s). Please reassign ownership first.")
                    return

                # Get user's tenant before deletion
                tenant = obj.tenant

                # Remove user from any groups
                obj.groups.clear()
                
                # Remove user permissions
                obj.user_permissions.clear()
                
                # Delete any invitations created by this user
                Invitation.objects.filter(invited_by=obj).delete()
                
                # Delete the user
                obj.delete()
                
                # If tenant exists and this was the last user, delete the tenant
                if tenant and not tenant.users.exists():
                    # Delete all tenant's invitations
                    tenant.invitations.all().delete()
                    # Delete all tenant's domains
                    tenant.tenant_domains.all().delete()
                    # Delete the tenant
                    tenant.delete()
                    messages.success(request, f"Deleted user {obj.email} and their tenant {tenant.name} (last user)")
                else:
                    messages.success(request, f"Successfully deleted user: {obj.email}")
            except Exception as e:
                messages.error(request, f"Error deleting user: {str(e)}")
                raise

# Register models with the custom admin site
admin_site.register(Tenant, TenantAdmin)
admin_site.register(Domain, DomainAdmin)
admin_site.register(Invitation, InvitationAdmin)
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Group, BaseGroupAdmin)  # Register the Group model with the default GroupAdmin

# Replace the default admin site
admin.site = admin_site
