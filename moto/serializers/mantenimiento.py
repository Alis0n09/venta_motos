from rest_framework import serializers
from moto.models import Mantenimiento


class MantenimientoSerializer(serializers.ModelSerializer):
    moto_detalle   = serializers.SerializerMethodField()
    cliente_nombre = serializers.SerializerMethodField()
    cliente_cedula = serializers.SerializerMethodField()

    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'moto',
            'moto_detalle',
            'cliente',
            'cliente_nombre',
            'cliente_cedula',
            'fecha',
            'tipo',
            'costo',
        ]
        read_only_fields = ['id']

    def get_moto_detalle(self, obj):
        if obj.moto and obj.moto.marca:
            return f"{obj.moto.marca.nombre} {obj.moto.modelo} ({obj.moto.anio})"
        return obj.moto.modelo if obj.moto else None

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None

    def get_cliente_cedula(self, obj):
        if obj.cliente:
            return obj.cliente.cedula
        return None

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value