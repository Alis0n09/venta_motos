from rest_framework import serializers
from moto.models import NotificacionesCliente


class NotificacionesClienteSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = NotificacionesCliente
        fields = ['id', 'cliente', 'tipo', 'mensaje', 'leido', 'fecha']

    def validate_tipo(self, value):
        if not value.strip():
            raise serializers.ValidationError("El tipo no puede estar vacío.")
        return value

    def validate_mensaje(self, value):
        if not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacío.")
        return value
