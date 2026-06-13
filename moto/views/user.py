from moto.models.usuario import Usuario
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from moto.serializers.user import (
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from moto.pagination import StandardPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset         = Usuario.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardPagination
    filter_backends  = [SearchFilter, OrderingFilter]
    search_fields    = ['username', 'email', 'first_name', 'last_name']
    ordering_fields  = ['username', 'email', 'date_joined']
    ordering         = ['username']

    def get_permissions(self):
        if self.action in ['profile', 'change_password']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'profile':
            return UserProfileSerializer
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer

    def get_queryset(self):
        qs = Usuario.objects.all()

        is_staff = self.request.query_params.get('is_staff')
        is_active = self.request.query_params.get('is_active')

        if is_staff is not None:
            qs = qs.filter(is_staff=is_staff.lower() == 'true')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        return qs

    @action(detail=False, methods=['get', 'patch'], url_path='profile', permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-active', permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'id': user.id, 'username': user.username, 'is_active': user.is_active})

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAdminUser])
    def stats(self, request):
        qs = Usuario.objects.all()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'inactive': qs.filter(is_active=False).count(),
            'staff': qs.filter(is_staff=True).count(),
            'detail': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined,
                }
                for user in qs.order_by('username')
            ],
        })