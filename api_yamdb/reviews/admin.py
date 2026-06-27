from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from reviews.models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка пользователя с полями role и bio."""

    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'is_superuser',
    )
    list_filter = ('role',)
    search_fields = ('username', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')
    search_fields = ('text',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
