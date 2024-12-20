# src/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Address

class AddressInline(admin.StackedInline):
    model = Address
    can_delete = True
    max_num = 1
    min_num = 0

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'tenant', 'is_staff', 'is_active')
    list_filter = ('email', 'is_staff', 'is_active', 'tenant')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'tenant')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'gender', 'address')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        (_('Preferences'), {'fields': ('preferred_language',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant', 'first_name', 'last_name', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)