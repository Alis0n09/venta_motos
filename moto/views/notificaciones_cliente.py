from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from moto.models import NotificacionesCliente
from moto.serializers.notificaciones_cliente import NotificacionesClienteSerializer
from moto.permissions import IsStaffOrReadOnly
from moto.filters import NotificacionesClienteFilter
from moto.pagination import StandardPagination


class NotificacionesClienteViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionesClienteSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotificacionesClienteFilter
    search_fields = ['tipo', 'mensaje', 'cliente__nombre', 'cliente__apellido']
    ordering_fields = ['fecha', 'tipo', 'leido']
    ordering = ['-fecha']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'mis_notificaciones', 'marcar_leida']:
            return [IsAuthenticated()]
        return [IsStaffOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = NotificacionesCliente.objects.select_related('cliente').all()

        if not user.is_staff and hasattr(user, 'perfil_cliente'):
            return qs.filter(cliente=user.perfil_cliente)

        return qs

    @action(
        detail=False,
        methods=['get'],
        url_path='mis-notificaciones',
        permission_classes=[IsAuthenticated]
    )
    def mis_notificaciones(self, request):
        """El cliente ve solo sus notificaciones."""
        if not hasattr(request.user, 'perfil_cliente'):
            return Response({'error': 'No tienes un perfil de cliente.'}, status=403)

        qs = NotificacionesCliente.objects.filter(
            cliente=request.user.perfil_cliente
        ).order_by('-fecha')

        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                NotificacionesClienteSerializer(page, many=True).data
            )
        return Response(NotificacionesClienteSerializer(qs, many=True).data)

    @action(
        detail=True,
        methods=['patch'],
        url_path='marcar-leida',
        permission_classes=[IsAuthenticated]
    )
    def marcar_leida(self, request, pk=None):
        """El cliente marca una notificación como leída."""
        notificacion = self.get_object()

        if not request.user.is_staff:
            if not hasattr(request.user, 'perfil_cliente'):
                return Response({'error': 'No tienes un perfil de cliente.'}, status=403)
            if notificacion.cliente != request.user.perfil_cliente:
                return Response({'error': 'No puedes marcar esta notificación.'}, status=403)

        notificacion.leido = True
        notificacion.save()
        return Response({'mensaje': 'Notificación marcada como leída.', 'id': notificacion.id})

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'no_leidas': qs.filter(leido=False).count(),
            'detail': [
                {
                    'id': n.id,
                    'cliente_id': n.cliente_id,
                    'tipo': n.tipo,
                    'leido': n.leido,
                    'fecha': n.fecha,
                }
                for n in qs.order_by('-fecha')
            ],
        })