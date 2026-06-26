from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from moto.models import Compra
from moto.serializers.compra import CompraSerializer
from moto.permissions import IsBodegueroOrAdmin
from moto.filters import CompraFilter
from moto.pagination import StandardPagination


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.select_related('proveedor', 'sucursal_destino').all()
    serializer_class = CompraSerializer
    permission_classes = [IsBodegueroOrAdmin]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CompraFilter
    search_fields = ['proveedor__empresa', 'sucursal_destino__nombre']
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Compra.objects.all()
        agg = qs.aggregate(suma=Sum('total'))
        return Response({
            'total_registros': qs.count(),
            'suma_total': agg['suma'] or 0,
        })
