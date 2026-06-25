from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from moto.models import Mantenimiento
from moto.serializers import MantenimientoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import MantenimientoFilter
from moto.pagination import StandardPagination


class MantenimientoViewSet(viewsets.ModelViewSet):
    queryset = Mantenimiento.objects.select_related(
        'moto',
        'moto__marca',
        'cliente',
    ).all()
    serializer_class = MantenimientoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MantenimientoFilter
    search_fields = [
        'tipo',
        'moto__modelo',
        'moto__marca__nombre',
        'cliente__nombre',
        'cliente__apellido',
        'cliente__cedula',
    ]
    ordering_fields = ['fecha', 'costo']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Mantenimiento.objects.all()
        agg = qs.aggregate(total_gastado=Sum('costo'))
        return Response({
            'total_registros': qs.count(),
            'total_gastado': agg['total_gastado'] or 0,
        })