from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import SucursalStaff
from moto.serializers.sucursal_staff import SucursalStaffSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import SucursalStaffFilter


class SucursalStaffViewSet(viewsets.ModelViewSet):
    queryset = SucursalStaff.objects.select_related('staff', 'staff__usuario', 'sucursal').all()
    serializer_class = SucursalStaffSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SucursalStaffFilter

    search_fields = ['staff__usuario__first_name', 'staff__usuario__last_name', 'sucursal__nombre']

    ordering_fields = ['id', 'fecha_asignacion']

    ordering = ['id']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        asignaciones = SucursalStaff.objects.select_related('staff', 'staff__usuario', 'sucursal').all()

        return Response({
            'total': asignaciones.count(),
            'detail': [
                {
                    'id': a.id,
                    'staff': f"{a.staff.usuario.first_name} {a.staff.usuario.last_name}",
                    'sucursal': a.sucursal.nombre,
                    'fecha_asignacion': a.fecha_asignacion,
                }
                for a in asignaciones
            ]
        })