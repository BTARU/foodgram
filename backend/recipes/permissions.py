from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """Дает доступ если метод безопасный или пользователь автор/админ."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user == obj.author
                or request.user.is_staff
                or request.user.is_superuser
            )
        )
