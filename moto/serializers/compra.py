from rest_framework import serializers
from moto.models import Compra


class CompraSerializer(serializers.ModelSerializer):
    fecha = serializers.DateField(read_only=True)

    class Meta:
        model  = Compra
        fields = ['id', 'proveedor', 'sucursal_destino', 'fecha', 'total']

    def validate_total(self, value):
        if value < 0:
            raise serializers.ValidationError("El total no puede ser negativo.")
        return value
