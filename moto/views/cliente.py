from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from moto.models import Cliente
from moto.serializers.cliente import ClienteSerializer
from moto.serializers.venta import VentaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import ClienteFilter
from moto.pagination import StandardPagination
from moto.mixins import LogActividadMixin


class ClienteViewSet(LogActividadMixin, viewsets.ModelViewSet):
    log_entidad = 'Cliente'
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClienteFilter
    search_fields = ['nombre', 'apellido', 'cedula', 'correo', 'telefono']
    ordering_fields = ['nombre', 'apellido', 'cedula']
    ordering = ['nombre']

    @action(detail=True, methods=['get'], url_path='ventas')
    def ventas_cliente(self, request, pk=None):
        cliente = self.get_object()
        qs = cliente.ventas.all().order_by('-fecha_venta')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(VentaSerializer(page, many=True).data)
        return Response(VentaSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Cliente.objects.annotate(num_ventas=Count('ventas', distinct=True))
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': c.id,
                    'nombre': c.nombre,
                    'apellido': c.apellido,
                    'cedula': c.cedula,
                    'correo': c.correo,
                    'num_ventas': c.num_ventas,
                }
                for c in qs.order_by('nombre')
            ],
        })