from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class StyledFieldMixin:    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes to all form fields
        for field_name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing_classes} w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500'.strip()


class UserCreateForm(StyledFieldMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
        )
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'role': 'Role',
            'is_active': 'Active',
        }
        help_texts = {
            'role': 'Select manager or employee role.',
        }


class UserUpdateForm(StyledFieldMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
        )
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'role': 'Role',
            'is_active': 'Active',
        }

