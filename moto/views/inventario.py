from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Inventario
from moto.serializers.inventario import InventarioSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import InventarioFilter
from moto.mixins import LogActividadMixin


class InventarioViewSet(LogActividadMixin, viewsets.ModelViewSet):
    log_entidad = 'Inventario'
    queryset = Inventario.objects.select_related('moto', 'moto__marca', 'sucursal').all()
    serializer_class = InventarioSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventarioFilter
    search_fields = ['moto__modelo', 'moto__marca__nombre', 'sucursal__nombre', 'ubicacion_bodega']
    ordering_fields = ['id', 'cantidad', 'sucursal', 'moto']
    ordering = ['id']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        inventarios = Inventario.objects.select_related('moto', 'moto__marca', 'sucursal').all()
        return Response({
            'total': inventarios.count(),
            'detail': [
                {
                    'id': i.id,
                    'moto': f"{i.moto.marca.nombre} {i.moto.modelo}" if i.moto.marca else i.moto.modelo,
                    'sucursal': i.sucursal.nombre,
                    'cantidad': i.cantidad,
                    'ubicacion_bodega': i.ubicacion_bodega,
                }
                for i in inventarios
            ]
        })