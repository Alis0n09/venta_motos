# moto/views/detalle_venta.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import DetalleVenta
from moto.serializers.detalle_venta import DetalleVentaSerializer
from moto.permissions import IsVendedorOrAdmin
from moto.pagination import StandardPagination
from moto.filters import DetalleVentaFilter


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsVendedorOrAdmin]
    pagination_class = StandardPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = DetalleVentaFilter

    search_fields = [
        'moto__marca',
        'moto__modelo',
        'venta__cliente__nombre',
        'venta__cliente__apellido',
        'venta__cliente__cedula',
        'venta__vendedor__nombre',
        'venta__vendedor__apellido',
        'venta__vendedor__cedula',
    ]

    ordering_fields = [
        'id',
        'venta',
        'moto',
        'cantidad',
        'precio_unitario',
    ]

    ordering = ['id']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = DetalleVenta.objects.all()

        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': d.id,
                    'venta': d.venta.id if d.venta else None,
                    'moto': d.moto.id if d.moto else None,
                    'moto_nombre': f"{d.moto.marca} {d.moto.modelo}" if d.moto else None,
                    'cantidad': d.cantidad,
                    'precio_unitario': d.precio_unitario,
                    'subtotal': d.subtotal,
                }
                for d in qs.order_by('-id')
            ]
        })