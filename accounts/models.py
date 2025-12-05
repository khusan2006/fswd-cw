from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    #  Any superuser must always have the MANAGER role.
    class Roles(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        EMPLOYEE = 'employee', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE,
        help_text='Controls the permissions available in the UI.',
    )

    def is_manager(self) -> bool:
        """Return True when the user is a manager."""
        return self.role == self.Roles.MANAGER

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Roles.MANAGER
        if not self.has_usable_password():
            raise ValueError("Password is required for all users.")
        super().save(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        permissions = [
            ('manage_team', 'Can manage users and team settings'),
        ]
