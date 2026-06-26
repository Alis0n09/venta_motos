# moto/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsClienteOrStaff(BasePermission):
    """
    Clientes autenticados pueden crear reseñas.
    Solo staff puede editar o borrar.
    Cualquier autenticado puede leer.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_staff or hasattr(request.user, 'perfil_cliente')
        return bool(request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        if hasattr(request.user, 'perfil_cliente'):
            return obj.cliente == request.user.perfil_cliente
        return False


def _get_rol(user):
    """Helper para obtener el rol del staff."""
    if hasattr(user, 'perfil_staff'):
        return user.perfil_staff.rol
    return None


class IsAdminRol(BasePermission):
    """Solo el admin puede escribir. Cualquier autenticado puede leer."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _get_rol(request.user) == 'admin'


class IsVendedorOrAdmin(BasePermission):
    """Vendedor y admin pueden escribir. Cualquier autenticado puede leer."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _get_rol(request.user) in ['vendedor', 'admin']


class IsBodegueroOrAdmin(BasePermission):
    """Bodeguero y admin pueden escribir. Cualquier autenticado puede leer."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _get_rol(request.user) in ['bodeguero', 'admin']