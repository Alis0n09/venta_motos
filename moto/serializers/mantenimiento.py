from rest_framework import serializers
from moto.models import Mantenimiento


class MantenimientoSerializer(serializers.ModelSerializer):
    tipo_mantenimiento = serializers.CharField(required=False, default="preventivo")

    class Meta:
        model = Mantenimiento
        fields = [
            'id', 'posventa', 'moto', 'tipo_mantenimiento',
            'fecha_programada', 'fecha_realizacion', 'descripcion',
            'costo', 'estado', 'observaciones'
        ]

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value
