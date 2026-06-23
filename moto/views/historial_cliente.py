from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import HistorialCliente
from moto.serializers.historial_cliente import HistorialClienteSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import HistorialClienteFilter
from moto.pagination import StandardPagination


class HistorialClienteViewSet(viewsets.ModelViewSet):
    queryset = HistorialCliente.objects.select_related('cliente').all()
    serializer_class = HistorialClienteSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HistorialClienteFilter
    search_fields = ['tipo_evento', 'cliente__nombre', 'cliente__apellido']
    ordering_fields = ['fecha', 'tipo_evento']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = HistorialCliente.objects.select_related('cliente').all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': h.id,
                    'cliente_id': h.cliente_id,
                    'tipo_evento': h.tipo_evento,
                    'fecha': h.fecha,
                }
                for h in qs.order_by('-fecha')
            ],
        })
