from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import HistorialPrecio
from moto.serializers.historial_precio import HistorialPrecioSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import HistorialPrecioFilter


class HistorialPrecioViewSet(viewsets.ModelViewSet):
    queryset = HistorialPrecio.objects.select_related('moto', 'moto__marca', 'usuario').all()
    serializer_class = HistorialPrecioSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HistorialPrecioFilter

    search_fields = ['moto__modelo', 'moto__marca__nombre', 'usuario__first_name', 'usuario__last_name']

    ordering_fields = ['id', 'fecha', 'precio_anterior', 'precio_nuevo', 'moto']

    ordering = ['-fecha']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        historial = HistorialPrecio.objects.select_related('moto', 'moto__marca', 'usuario').all()

        return Response({
            'total': historial.count(),
            'detail': [
                {
                    'id': h.id,
                    'moto': f"{h.moto.marca.nombre} {h.moto.modelo}" if h.moto.marca else h.moto.modelo,
                    'precio_anterior': h.precio_anterior,
                    'precio_nuevo': h.precio_nuevo,
                    'fecha': h.fecha,
                    'usuario': f"{h.usuario.first_name} {h.usuario.last_name}" if h.usuario else None,
                }
                for h in historial
            ]
        })