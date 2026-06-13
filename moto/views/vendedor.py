from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import Staff
from moto.serializers.vendedor import VendedorSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.pagination import StandardPagination
from moto.filters import VendedorFilter


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.select_related('usuario').all()
    serializer_class = VendedorSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VendedorFilter

    search_fields = [
        'usuario__first_name',
        'usuario__last_name',
        'usuario__cedula',
        'usuario__email',
        'usuario__telefono',
    ]

    ordering_fields = [
        'id',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__cedula',
    ]

    ordering = ['id']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        vendedores = Staff.objects.select_related('usuario').annotate(
            total_ventas=Count('ventas_realizadas')
        )

        return Response({
            'total': vendedores.count(),
            'detail': [
                {
                    'id': v.id,
                    'nombre': v.usuario.first_name,
                    'apellido': v.usuario.last_name,
                    'cedula': v.usuario.cedula,
                    'telefono': v.usuario.telefono,
                    'correo': v.usuario.email,
                    'rol': v.rol,
                    'total_ventas': v.total_ventas,
                }
                for v in vendedores
            ]
        })