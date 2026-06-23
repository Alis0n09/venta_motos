from rest_framework import serializers
from moto.models import Financiamiento


class FinanciamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Financiamiento
        fields = '__all__'
        read_only_fields = ['id']

    def validate_monto_financiado(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto financiado debe ser mayor a cero.")
        return value

    def validate_tasa_interes(self, value):
        if value < 0:
            raise serializers.ValidationError("La tasa de interés no puede ser negativa.")
        return value

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return data
