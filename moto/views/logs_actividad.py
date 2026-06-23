from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import LogsActividad
from moto.serializers.logs_actividad import LogsActividadSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import LogsActividadFilter
from moto.pagination import StandardPagination


class LogsActividadViewSet(viewsets.ModelViewSet):
    queryset = LogsActividad.objects.select_related('usuario').all()
    serializer_class = LogsActividadSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LogsActividadFilter
    search_fields = ['accion', 'entidad', 'usuario__username']
    ordering_fields = ['fecha', 'accion', 'entidad']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = LogsActividad.objects.select_related('usuario').all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': log.id,
                    'usuario_id': log.usuario_id,
                    'accion': log.accion,
                    'entidad': log.entidad,
                    'fecha': log.fecha,
                }
                for log in qs.order_by('-fecha')
            ],
        })
