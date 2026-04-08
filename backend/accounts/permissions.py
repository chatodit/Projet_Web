from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrEditor(BasePermission):
    """Allow write access to ADMIN, EDITOR or SUPERUSER."""

    def has_permission(self, request, view):
        # Tout le monde peut LIRE (GET, HEAD, OPTIONS) s'il est connecté
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Pour MODIFIER/SUPPRIMER :
        return (
            request.user and request.user.is_authenticated and (
                request.user.is_superuser or # On ajoute ça !
                getattr(request.user, 'is_admin_or_editor', False) or
                request.user.role in ["admin", "editor"] # Sécurité selon ton modèle
            )
        )

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and (
                request.user.is_superuser or # Le superuser est par défaut admin
                request.user.role == "admin"
            )
        )