from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Repuesto
from moto.serializers.repuesto import RepuestoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import RepuestoFilter


class RepuestoViewSet(viewsets.ModelViewSet):
    queryset = Repuesto.objects.select_related('marca_compatible').all()
    serializer_class = RepuestoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RepuestoFilter

    search_fields = ['nombre', 'marca_compatible__nombre']

    ordering_fields = ['id', 'nombre', 'stock', 'precio']

    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        repuestos = Repuesto.objects.select_related('marca_compatible').all()

        return Response({
            'total': repuestos.count(),
            'detail': [
                {
                    'id': r.id,
                    'nombre': r.nombre,
                    'marca_compatible': r.marca_compatible.nombre if r.marca_compatible else None,
                    'stock': r.stock,
                    'precio': r.precio,
                }
                for r in repuestos
            ]
        })