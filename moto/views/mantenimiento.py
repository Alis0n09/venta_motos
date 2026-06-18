from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Mantenimiento
from moto.serializers import MantenimientoSerializer
from moto.pagination import StandardPagination
from moto.permissions import IsStaffOrReadOnly
from moto.filters import MantenimientoFilter


class MantenimientoViewSet(viewsets.ModelViewSet):
    queryset = Mantenimiento.objects.select_related('posventa', 'moto').all()
    serializer_class = MantenimientoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MantenimientoFilter
    search_fields = ['descripcion', 'observaciones', 'tipo_mantenimiento', 'estado']
    ordering_fields = ['fecha_programada', 'fecha_realizacion', 'costo', 'estado']
    ordering = ['-fecha_programada']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Mantenimiento.objects.count()
        return Response({
            'total': total,
            'detail': {
                'pendientes': Mantenimiento.objects.filter(estado='pendiente').count(),
                'en_proceso': Mantenimiento.objects.filter(estado='en_proceso').count(),
                'completados': Mantenimiento.objects.filter(estado='completado').count(),
                'cancelados': Mantenimiento.objects.filter(estado='cancelado').count(),
            }
        })
