from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrEditor(BasePermission):
    """Allow write access only to users with ADMIN or EDITOR role."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_or_editor
        )


class IsAdminOnly(BasePermission):
    """Allow access only to users with the ADMIN role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )
