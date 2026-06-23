from rest_framework import serializers
from moto.models import Garantia


class GarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantia
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        if data.get('fecha_fin') and data.get('fecha_inicio') and data['fecha_fin'] < data['fecha_inicio']:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return data
