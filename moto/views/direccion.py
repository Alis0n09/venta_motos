from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models                import Direccion
from moto.serializers.direccion import DireccionSerializer
from moto.permissions           import IsStaffOrReadOnly
from moto.filters               import DireccionFilter
from moto.pagination            import StandardPagination


class DireccionViewSet(viewsets.ModelViewSet):
    queryset           = Direccion.objects.select_related('cliente').all()
    serializer_class   = DireccionSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = DireccionFilter
    search_fields      = ['calle', 'ciudad', 'provincia']
    ordering_fields    = ['ciudad', 'provincia', 'principal']
    ordering           = ['ciudad']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Direccion.objects.select_related('cliente').all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': d.id,
                    'cliente_id': d.cliente_id,
                    'calle': d.calle,
                    'ciudad': d.ciudad,
                    'provincia': d.provincia,
                    'principal': d.principal,
                }
                for d in qs.order_by('ciudad')
            ]
        })
