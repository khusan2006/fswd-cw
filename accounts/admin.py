from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')

    def has_delete_permission(self, request, obj=None):
        # Prevent non-superusers from deleting manager accounts in the admin.  
        base_allowed = super().has_delete_permission(request, obj)
        if not base_allowed:
            return False
        if obj is None:
            return True
        if isinstance(obj, User) and obj.is_manager() and not request.user.is_superuser:
            return False
        return True
