from rest_framework import serializers
from moto.models import CuotaPago


class CuotaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaPago
        fields = '__all__'
        read_only_fields = ['id']

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto de la cuota debe ser mayor a cero.")
        return value

    def validate(self, data):
        fecha_vencimiento = data.get('fecha_vencimiento')
        fecha_pago = data.get('fecha_pago')
        if fecha_vencimiento and fecha_pago and fecha_pago < fecha_vencimiento:
            raise serializers.ValidationError(
                {"fecha_pago": "La fecha de pago no puede ser anterior a la fecha de vencimiento."}
            )
        return data
