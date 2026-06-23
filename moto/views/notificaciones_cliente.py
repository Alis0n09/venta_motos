from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import NotificacionesCliente
from moto.serializers.notificaciones_cliente import NotificacionesClienteSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import NotificacionesClienteFilter
from moto.pagination import StandardPagination


class NotificacionesClienteViewSet(viewsets.ModelViewSet):
    queryset = NotificacionesCliente.objects.select_related('cliente').all()
    serializer_class = NotificacionesClienteSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotificacionesClienteFilter
    search_fields = ['tipo', 'mensaje', 'cliente__nombre', 'cliente__apellido']
    ordering_fields = ['fecha', 'tipo', 'leido']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = NotificacionesCliente.objects.select_related('cliente').all()
        return Response({
            'total': qs.count(),
            'no_leidas': qs.filter(leido=False).count(),
            'detail': [
                {
                    'id': n.id,
                    'cliente_id': n.cliente_id,
                    'tipo': n.tipo,
                    'leido': n.leido,
                    'fecha': n.fecha,
                }
                for n in qs.order_by('-fecha')
            ],
        })
