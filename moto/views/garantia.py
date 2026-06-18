from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Garantia
from moto.serializers import GarantiaSerializer
from moto.pagination import StandardPagination
from moto.permissions import IsStaffOrReadOnly
from moto.filters import GarantiaFilter


class GarantiaViewSet(viewsets.ModelViewSet):
    queryset = Garantia.objects.select_related('posventa').all()
    serializer_class = GarantiaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GarantiaFilter
    search_fields = ['tipo_cobertura', 'detalles', 'estado']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'estado']
    ordering = ['-fecha_inicio']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Garantia.objects.count()
        return Response({
            'total': total,
            'detail': {
                'activas': Garantia.objects.filter(estado='activa').count(),
                'expiradas': Garantia.objects.filter(estado='expirada').count(),
                'canceladas': Garantia.objects.filter(estado='cancelada').count(),
            }
        })
