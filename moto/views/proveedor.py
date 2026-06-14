from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models                import Proveedor
from moto.serializers.proveedor import ProveedorSerializer
from moto.permissions           import IsStaffOrReadOnly
from moto.filters               import ProveedorFilter
from moto.pagination            import StandardPagination


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset           = Proveedor.objects.all()
    serializer_class   = ProveedorSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = ProveedorFilter
    search_fields      = ['empresa', 'contacto', 'pais', 'correo']
    ordering_fields    = ['empresa', 'pais']
    ordering           = ['empresa']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = Proveedor.objects.all()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': p.id,
                    'empresa': p.empresa,
                    'contacto': p.contacto,
                    'correo': p.correo,
                    'pais': p.pais,
                }
                for p in qs.order_by('empresa')
            ]
        })
