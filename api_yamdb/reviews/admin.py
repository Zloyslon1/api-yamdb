from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка кастомного пользователя с полями role и bio."""

    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'is_superuser',
    )
    list_filter = ('role',)
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'bio')}),
    )
