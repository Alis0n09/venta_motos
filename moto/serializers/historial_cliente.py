from rest_framework import serializers
from moto.models import HistorialCliente


class HistorialClienteSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = HistorialCliente
        fields = ['id', 'cliente', 'tipo_evento', 'detalle', 'fecha']

    def validate_tipo_evento(self, value):
        if not value.strip():
            raise serializers.ValidationError("El tipo de evento no puede estar vacío.")
        return value
