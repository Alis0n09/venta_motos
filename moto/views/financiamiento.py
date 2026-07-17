from decimal import Decimal, InvalidOperation
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from moto.models import Financiamiento
from moto.serializers import FinanciamientoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import FinanciamientoFilter
from moto.pagination import StandardPagination
from moto.mixins import LogActividadMixin


class FinanciamientoViewSet(LogActividadMixin, viewsets.ModelViewSet):
    log_entidad = 'Financiamiento'
    queryset = Financiamiento.objects.select_related(
        'venta', 'venta__cliente',
    ).prefetch_related('venta__detalles__moto__marca').all()
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
            'pendientes': qs.filter(estado='pendiente').count(),
            'activos': qs.filter(estado='activo').count(),
            'pagados': qs.filter(estado='pagado').count(),
            'cancelados': qs.filter(estado='cancelado').count(),
        })

    @action(detail=True, methods=['patch'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        """El admin aprueba una solicitud de financiamiento del cliente,
        fijando la tasa de interés (el cliente nunca la elige). Solo aplica
        a financiamientos en estado 'pendiente'; al aprobar, el signal
        generar_cuotas_financiamiento arma el plan de cuotas con esa tasa."""
        financiamiento = self.get_object()
        if financiamiento.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden aprobar financiamientos en estado pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tasa_interes = request.data.get('tasa_interes')
        if tasa_interes is None:
            return Response(
                {'tasa_interes': 'Debes indicar la tasa de interés anual para aprobar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            tasa_interes = Decimal(str(tasa_interes))
        except (InvalidOperation, TypeError):
            return Response(
                {'tasa_interes': 'La tasa de interés debe ser un número válido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if tasa_interes < 0:
            return Response(
                {'tasa_interes': 'La tasa de interés no puede ser negativa.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        financiamiento.tasa_interes = tasa_interes
        financiamiento.estado = 'activo'
        financiamiento.save()
        return Response(FinanciamientoSerializer(financiamiento).data)

    @action(detail=True, methods=['patch'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """El admin rechaza una solicitud de financiamiento del cliente.
        Solo aplica a financiamientos en estado 'pendiente'."""
        financiamiento = self.get_object()
        if financiamiento.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden rechazar financiamientos en estado pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        financiamiento.estado = 'cancelado'
        financiamiento.save()
        return Response(FinanciamientoSerializer(financiamiento).data)