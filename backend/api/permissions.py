"""Project custom permissions."""
from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """Gives permission if method is save or user are author of obj/admin."""

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
