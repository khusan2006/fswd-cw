from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import UserCreateForm, UserUpdateForm
from .mixins import RolePermissionRequiredMixin
from .models import User


def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    # Add Tailwind classes to form fields
    for field in form.fields.values():
        field.widget.attrs['class'] = 'w-full rounded border-slate-300 focus:border-slate-500 focus:ring-slate-500'
    
    return render(request, 'registration/login.html', {'form': form})


class UserListView(LoginRequiredMixin, RolePermissionRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'accounts/user_list.html'
    ordering = ['-date_joined']
    permission_required = 'accounts.manage_team'


class UserCreateView(LoginRequiredMixin, RolePermissionRequiredMixin, CreateView):
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user-list')
    permission_required = 'accounts.manage_team'

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user-list')
    permission_required = 'accounts.manage_team'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'User updated successfully.')
        return redirect(self.success_url)


class UserDeactivateView(LoginRequiredMixin, RolePermissionRequiredMixin, View):
    permission_required = 'accounts.manage_team'
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
        elif user.is_manager() and not request.user.is_superuser:
            # Prevent managers from deactivating other managers; only superusers can.
            messages.error(request, 'Only a superuser can deactivate another manager.')
        else:
            user.is_active = False
            user.save(update_fields=['is_active'])
            messages.info(request, 'User deactivated.')
        return redirect('user-list')
