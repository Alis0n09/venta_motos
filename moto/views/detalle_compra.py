from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import DetalleCompra
from moto.serializers.detalle_compra import DetalleCompraSerializer
from moto.permissions import IsBodegueroOrAdmin
from moto.filters import DetalleCompraFilter
from moto.pagination import StandardPagination


class DetalleCompraViewSet(viewsets.ModelViewSet):
    queryset = DetalleCompra.objects.select_related('compra', 'moto').all()
    serializer_class = DetalleCompraSerializer
    permission_classes = [IsBodegueroOrAdmin]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DetalleCompraFilter
    search_fields = ['moto__marca__nombre', 'moto__modelo']
    ordering_fields = ['cantidad', 'precio_costo']
    ordering = ['id']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = DetalleCompra.objects.all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': d.id,
                    'moto_id': d.moto_id,
                    'cantidad': d.cantidad,
                    'precio_costo': d.precio_costo,
                }
                for d in qs.order_by('id')
            ],
        })
