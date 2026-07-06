from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from moto.serializers.user import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from moto.serializers.user import RegisterSerializer, RegisterStaffSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
        description='Registro de cliente. Crea automáticamente un perfil de Cliente asociado.'
    )
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

    @extend_schema(
        request=RegisterStaffSerializer,
        responses={201: RegisterStaffSerializer},
        description='Registro de staff (admin/vendedor/bodeguero). Solo accesible por administradores.'
    )
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

    @extend_schema(
        description='Cierra la sesión del usuario invalidando el refresh token.'
    )
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
    
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        codigo = f"{uid}.{token}"

        context = {
            'nombre': user.first_name or user.username,
            'codigo': codigo,
        }

        html_content = render_to_string('emails/password_reset.html', context)
        text_content = (
            f"Hola {user.first_name or user.username},\n\n"
            f"Usa este código en la app para restablecer tu contraseña:\n\n{codigo}\n\n"
            f"Si no solicitaste esto, ignora este correo."
        )

        email = EmailMultiAlternatives(
            subject='Recupera tu contraseña — Victal Speed',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)

        return Response({'message': 'Se envió un código a tu correo registrado.'})

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Contraseña actualizada correctamente.'})