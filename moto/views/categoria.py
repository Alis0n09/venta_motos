from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Categoria
from moto.serializers.categoria import CategoriaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import CategoriaFilter


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoriaFilter

    search_fields = ['nombre', 'descripcion']

    ordering_fields = ['id', 'nombre']

    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        categorias = Categoria.objects.all()

        return Response({
            'total': categorias.count(),
            'detail': [
                {
                    'id': c.id,
                    'nombre': c.nombre,
                    'descripcion': c.descripcion,
                }
                for c in categorias
            ]
        })