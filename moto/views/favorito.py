# moto/views/favorito.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from moto.models import Favorito, Moto
from moto.serializers.favorito import FavoritoSerializer
from moto.pagination import StandardPagination


class FavoritoViewSet(viewsets.ModelViewSet):
    """
    Favoritos del cliente autenticado. Cada cliente solo puede ver y
    modificar sus propios favoritos (no hay acceso de staff a esto, es
    estrictamente personal, como una lista de deseos).
    """
    serializer_class = FavoritoSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'perfil_cliente'):
            return Favorito.objects.none()
        return Favorito.objects.select_related('moto', 'moto__marca').filter(
            cliente=user.perfil_cliente
        )

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.perfil_cliente)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        Agrega o quita una moto de favoritos en un solo request, pensado
        para el clic del corazón en el frontend: si ya estaba, la quita;
        si no estaba, la agrega. Body: {"moto_id": <id>}
        """
        if not hasattr(request.user, 'perfil_cliente'):
            return Response(
                {'error': 'No tienes un perfil de cliente.'},
                status=status.HTTP_403_FORBIDDEN
            )

        moto_id = request.data.get('moto_id')
        if not moto_id:
            return Response(
                {'error': 'moto_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            moto = Moto.objects.get(id=moto_id)
        except Moto.DoesNotExist:
            return Response(
                {'error': 'Moto no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cliente = request.user.perfil_cliente
        favorito_existente = Favorito.objects.filter(cliente=cliente, moto=moto).first()

        if favorito_existente:
            favorito_existente.delete()
            return Response({'favorito': False})

        nuevo = Favorito.objects.create(cliente=cliente, moto=moto)
        return Response(
            {'favorito': True, 'data': FavoritoSerializer(nuevo).data},
            status=status.HTTP_201_CREATED,
        )