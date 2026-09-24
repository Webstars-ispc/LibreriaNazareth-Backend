from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """Solo deja pasar a usuarios que pertenecen al grupo 'Administrador'"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Administrador').exists()
        )
        
class IsAdminOrReadOnly(BasePermission):
    """
    Permite lectura (GET, HEAD, OPTIONS) a cualquier usuario autenticado.
    Solo el Administrador puede modificar o eliminar.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.groups.filter(name='Administrador').exists()