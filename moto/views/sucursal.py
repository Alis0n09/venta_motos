from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models                import Sucursal
from moto.serializers.sucursal  import SucursalSerializer
from moto.permissions           import IsStaffOrReadOnly
from moto.filters               import SucursalFilter
from moto.pagination            import StandardPagination


class SucursalViewSet(viewsets.ModelViewSet):
    queryset           = Sucursal.objects.all()
    serializer_class   = SucursalSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = SucursalFilter
    search_fields      = ['nombre', 'ciudad', 'direccion']
    ordering_fields    = ['nombre', 'ciudad']
    ordering           = ['nombre']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Sucursal.objects.all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': s.id,
                    'nombre': s.nombre,
                    'ciudad': s.ciudad,
                    'direccion': s.direccion,
                    'telefono': s.telefono,
                }
                for s in qs.order_by('nombre')
            ]
        })
