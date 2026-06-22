from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Resena
from moto.serializers.resena import ResenaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import ResenaFilter


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related('moto', 'moto__marca', 'cliente').all()
    serializer_class = ResenaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ResenaFilter

    search_fields = ['moto__modelo', 'moto__marca__nombre', 'cliente__nombre', 'cliente__apellido', 'comentario']

    ordering_fields = ['id', 'fecha', 'rating', 'moto', 'cliente']

    ordering = ['-fecha']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        resenas = Resena.objects.select_related('moto', 'moto__marca', 'cliente').all()

        return Response({
            'total': resenas.count(),
            'promedio_rating': round(
                sum(r.rating for r in resenas) / resenas.count(), 2
            ) if resenas.count() > 0 else 0,
            'detail': [
                {
                    'id': r.id,
                    'moto': f"{r.moto.marca.nombre} {r.moto.modelo}" if r.moto.marca else r.moto.modelo,
                    'cliente': f"{r.cliente.nombre} {r.cliente.apellido}",
                    'rating': r.rating,
                    'comentario': r.comentario,
                    'fecha': r.fecha,
                }
                for r in resenas
            ]
        })