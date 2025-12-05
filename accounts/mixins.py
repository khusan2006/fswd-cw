from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect


class RolePermissionRequiredMixin(PermissionRequiredMixin):

    permission_denied_message = 'You need manager access to perform this action.'
    raise_exception = False

    def has_permission(self):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.is_manager()):
            return True
        return super().has_permission()

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('dashboard')

