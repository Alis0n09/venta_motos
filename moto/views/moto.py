from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Moto
from moto.serializers.moto import MotoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import MotoFilter


class MotoViewSet(viewsets.ModelViewSet):
    queryset = Moto.objects.select_related('marca', 'categoria').all()
    serializer_class = MotoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MotoFilter

    search_fields = [
        'marca__nombre',
        'modelo',
        'color',
        'estado',
    ]

    ordering_fields = [
        'id',
        'marca',
        'modelo',
        'anio',
        'precio',
        'stock',
        'cilindraje',
        'estado',
    ]

    ordering = ['id']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        motos = Moto.objects.select_related('marca', 'categoria').all()

        return Response({
            'total': motos.count(),
            'detail': [
                {
                    'id': m.id,
                    'marca': m.marca.nombre if m.marca else None,
                    'categoria': m.categoria.nombre if m.categoria else None,
                    'modelo': m.modelo,
                    'anio': m.anio,
                    'color': m.color,
                    'precio': m.precio,
                    'stock': m.stock,
                    'cilindraje': m.cilindraje,
                    'estado': m.estado,
                }
                for m in motos
            ]
        })