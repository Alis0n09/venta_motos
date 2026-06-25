from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from moto.models import Financiamiento
from moto.serializers import FinanciamientoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import FinanciamientoFilter
from moto.pagination import StandardPagination


class FinanciamientoViewSet(viewsets.ModelViewSet):
    queryset = Financiamiento.objects.select_related(
        'venta',
        'venta__cliente',
    ).prefetch_related(
        'venta__detalles__moto__marca'
    ).all()
    serializer_class = FinanciamientoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FinanciamientoFilter
    search_fields = ['estado', 'venta__cliente__nombre', 'venta__cliente__apellido', 'venta__cliente__cedula']
    ordering_fields = ['fecha_inicio', 'monto_financiado', 'estado']
    ordering = ['-fecha_inicio']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Financiamiento.objects.all()
        agg = qs.aggregate(total_financiado=Sum('monto_financiado'))
        return Response({
            'total_registros': qs.count(),
            'total_financiado': agg['total_financiado'] or 0,
            'activos': qs.filter(estado='activo').count(),
            'pagados': qs.filter(estado='pagado').count(),
            'cancelados': qs.filter(estado='cancelado').count(),
        })