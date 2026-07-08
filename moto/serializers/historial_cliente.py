from rest_framework import serializers
from moto.models import HistorialCliente


class HistorialClienteSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    cliente_cedula = serializers.SerializerMethodField()

    class Meta:
        model  = HistorialCliente
        fields = ['id', 'cliente', 'cliente_nombre', 'cliente_cedula', 'tipo_evento', 'detalle', 'fecha']

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None

    def get_cliente_cedula(self, obj):
        return obj.cliente.cedula if obj.cliente else None

    def validate_tipo_evento(self, value):
        if not value.strip():
            raise serializers.ValidationError("El tipo de evento no puede estar vacío.")
        return value