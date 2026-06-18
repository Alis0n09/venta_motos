from rest_framework import serializers
from moto.models import Garantia


class GarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantia
        fields = [
            'id', 'posventa', 'fecha_inicio', 'fecha_fin',
            'tipo_cobertura', 'detalles', 'estado'
        ]

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return data
