from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import Category, Genre, Title, User


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    list_filter = ('category', 'genre')
    search_fields = ('name',)
