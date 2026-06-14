from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Marca
from moto.serializers.marca import MarcaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import MarcaFilter


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MarcaFilter

    search_fields = ['nombre', 'pais_origen']

    ordering_fields = ['id', 'nombre', 'pais_origen', 'activa']

    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        marcas = Marca.objects.all()

        return Response({
            'total': marcas.count(),
            'activas': marcas.filter(activa=True).count(),
            'detail': [
                {
                    'id': m.id,
                    'nombre': m.nombre,
                    'pais_origen': m.pais_origen,
                    'activa': m.activa,
                }
                for m in marcas
            ]
        })