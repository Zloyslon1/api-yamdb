from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только администратору (или суперюзеру)."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(IsAdmin):
    """Читать может любой, изменять — только администратор."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """Чтение — всем; запись — автору, модератору или админу."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
