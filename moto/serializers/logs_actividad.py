from rest_framework import serializers
from moto.models import LogsActividad


class LogsActividadSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = LogsActividad
        fields = ['id', 'usuario', 'accion', 'entidad', 'datos_antes', 'datos_despues', 'fecha']

    def validate_accion(self, value):
        if not value.strip():
            raise serializers.ValidationError("La acción no puede estar vacía.")
        return value

    def validate_entidad(self, value):
        if not value.strip():
            raise serializers.ValidationError("La entidad no puede estar vacía.")
        return value
