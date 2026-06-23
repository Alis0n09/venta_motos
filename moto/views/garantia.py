from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Garantia
from moto.serializers import GarantiaSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import GarantiaFilter
from moto.pagination import StandardPagination


class GarantiaViewSet(viewsets.ModelViewSet):
    queryset = Garantia.objects.select_related('venta').all()
    serializer_class = GarantiaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GarantiaFilter
    search_fields = ['tipo']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_inicio']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Garantia.objects.all()
        return Response({
            'total_registros': qs.count(),
        })
