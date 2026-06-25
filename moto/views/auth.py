# moto/views/auth.py

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from moto.serializers.user import RegisterSerializer, RegisterStaffSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'access':   str(refresh.access_token),
            'refresh':  str(refresh),
            'user_id':  user.id,
            'username': user.username,
            'email':    user.email,
            'is_staff': user.is_staff,
        }, status=status.HTTP_201_CREATED)


class RegisterStaffView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = RegisterStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user_id':  user.id,
            'username': user.username,
            'email':    user.email,
            'nombre':   user.first_name,
            'apellido': user.last_name,
            'rol':      user.perfil_staff.rol,
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {'error': 'Token is invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'message': 'Session closed successfully.'},
            status=status.HTTP_200_OK
        )