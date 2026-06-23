from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from moto.models import CuotaPago
from moto.serializers import CuotaPagoSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import CuotaPagoFilter
from moto.pagination import StandardPagination


class CuotaPagoViewSet(viewsets.ModelViewSet):
    queryset = CuotaPago.objects.select_related('financiamiento').all()
    serializer_class = CuotaPagoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CuotaPagoFilter
    search_fields = ['estado']
    ordering_fields = ['fecha_vencimiento', 'monto', 'numero_cuota', 'estado']
    ordering = ['financiamiento', 'numero_cuota']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = CuotaPago.objects.all()
        agg_pagado = qs.filter(estado='pagada').aggregate(total=Sum('monto'))
        agg_pendiente = qs.filter(estado='pendiente').aggregate(total=Sum('monto'))
        return Response({
            'total_registros': qs.count(),
            'pagadas': qs.filter(estado='pagada').count(),
            'pendientes': qs.filter(estado='pendiente').count(),
            'vencidas': qs.filter(estado='vencida').count(),
            'total_pagado': agg_pagado['total'] or 0,
            'total_pendiente': agg_pendiente['total'] or 0,
        })
