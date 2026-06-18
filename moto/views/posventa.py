from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Posventa
from moto.serializers import PosventaSerializer
from moto.pagination import StandardPagination
from moto.permissions import IsStaffOrReadOnly
from moto.filters import PosventaFilter


class PosventaViewSet(viewsets.ModelViewSet):
    queryset = Posventa.objects.select_related('venta').all()
    serializer_class = PosventaSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PosventaFilter
    search_fields = ['observaciones', 'estado']
    ordering_fields = ['fecha_apertura', 'estado']
    ordering = ['-fecha_apertura']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Posventa.objects.count()
        return Response({
            'total': total,
            'detail': {
                'pendientes': Posventa.objects.filter(estado='pendiente').count(),
                'en_proceso': Posventa.objects.filter(estado='en_proceso').count(),
                'finalizados': Posventa.objects.filter(estado='finalizado').count(),
                'cancelados': Posventa.objects.filter(estado='cancelado').count(),
            }
        })
