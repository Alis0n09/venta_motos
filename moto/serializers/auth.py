# moto/serializers/auth.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email']    = user.email
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id']  = self.user.id
        data['username'] = self.user.username
        data['email']    = self.user.email
        data['is_staff'] = self.user.is_staff

        # Registrar log de login
        try:
            from moto.models import LogsActividad
            LogsActividad.objects.create(
                usuario=self.user,
                accion='LOGIN',
                entidad='Usuario',
                datos_antes=None,
                datos_despues={
                    'username': self.user.username,
                    'email': self.user.email,
                    'is_staff': self.user.is_staff,
                }
            )
        except Exception:
            pass

        return data


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer