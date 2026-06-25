from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import HistorialCliente
from moto.serializers.historial_cliente import HistorialClienteSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import HistorialClienteFilter
from moto.pagination import StandardPagination


class HistorialClienteViewSet(viewsets.ModelViewSet):
    serializer_class = HistorialClienteSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HistorialClienteFilter
    search_fields = ['tipo_evento', 'cliente__nombre', 'cliente__apellido']
    ordering_fields = ['fecha', 'tipo_evento']
    ordering = ['-fecha']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'mi_historial']:
            return [IsAuthenticated()]
        return [IsStaffOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = HistorialCliente.objects.select_related('cliente').all()

        # Si es cliente, solo ve su propio historial
        if not user.is_staff and hasattr(user, 'perfil_cliente'):
            return qs.filter(cliente=user.perfil_cliente)

        # Si es staff ve todo
        return qs

    @action(
        detail=False,
        methods=['get'],
        url_path='mi-historial',
        permission_classes=[IsAuthenticated]
    )
    def mi_historial(self, request):
        """Endpoint específico para que el cliente vea su historial."""
        if not hasattr(request.user, 'perfil_cliente'):
            return Response({'error': 'No tienes un perfil de cliente.'}, status=403)

        qs = HistorialCliente.objects.filter(
            cliente=request.user.perfil_cliente
        ).order_by('-fecha')

        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                HistorialClienteSerializer(page, many=True).data
            )
        return Response(HistorialClienteSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'detail': [
                {
                    'id': h.id,
                    'cliente_id': h.cliente_id,
                    'tipo_evento': h.tipo_evento,
                    'fecha': h.fecha,
                }
                for h in qs.order_by('-fecha')
            ],
        })