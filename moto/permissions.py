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
            return True
        return bool(request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        if hasattr(request.user, 'perfil_cliente'):
            return obj.cliente == request.user.perfil_cliente
        return False