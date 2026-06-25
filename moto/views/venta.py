from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Venta
from moto.serializers.venta import VentaSerializer, CrearVentaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import VentaFilter
from moto.mixins import LogActividadMixin


class VentaViewSet(LogActividadMixin, viewsets.ModelViewSet):
    log_entidad = 'Venta'
    queryset = Venta.objects.select_related('cliente', 'vendedor', 'vendedor__usuario').prefetch_related('detalles__moto__marca').all()
    serializer_class = VentaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VentaFilter

    search_fields = [
        'cliente__nombre', 'cliente__apellido', 'cliente__cedula',
        'cliente__correo', 'vendedor__usuario__first_name',
        'vendedor__usuario__last_name', 'vendedor__usuario__cedula',
        'vendedor__usuario__email', 'metodo_pago',
    ]
    ordering_fields = ['id', 'fecha_venta', 'total', 'metodo_pago', 'cliente', 'vendedor']
    ordering = ['id']

    @action(detail=False, methods=['post'], url_path='comprar', permission_classes=[IsAuthenticated])
    def comprar(self, request):
        if not hasattr(request.user, 'perfil_cliente'):
            return Response({'error': 'Solo los clientes registrados pueden realizar compras.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CrearVentaSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        venta = serializer.save()

        return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='mis-compras', permission_classes=[IsAuthenticated])
    def mis_compras(self, request):
        if not hasattr(request.user, 'perfil_cliente'):
            return Response({'error': 'No tienes un perfil de cliente.'}, status=status.HTTP_403_FORBIDDEN)

        ventas = Venta.objects.filter(
            cliente=request.user.perfil_cliente
        ).select_related('cliente', 'vendedor', 'vendedor__usuario').prefetch_related('detalles__moto__marca').order_by('-fecha_venta')

        page = self.paginate_queryset(ventas)
        if page is not None:
            return self.get_paginated_response(VentaSerializer(page, many=True).data)
        return Response(VentaSerializer(ventas, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        ventas = Venta.objects.select_related('cliente', 'vendedor', 'vendedor__usuario').all()
        return Response({
            'total': ventas.count(),
            'detail': [
                {
                    'id': v.id,
                    'cliente': v.cliente.id if v.cliente else None,
                    'cliente_nombre': f"{v.cliente.nombre} {v.cliente.apellido}" if v.cliente else None,
                    'vendedor': v.vendedor.id if v.vendedor else None,
                    'vendedor_nombre': f"{v.vendedor.usuario.first_name} {v.vendedor.usuario.last_name}" if v.vendedor else None,
                    'fecha_venta': v.fecha_venta,
                    'metodo_pago': v.metodo_pago,
                    'total': v.total,
                }
                for v in ventas
            ]
        })