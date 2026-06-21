from rest_framework import serializers
from moto.models import DetalleCompra


class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DetalleCompra
        fields = ['id', 'compra', 'moto', 'cantidad', 'precio_costo']

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value

    def validate_precio_costo(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de costo debe ser mayor que cero.")
        return value
