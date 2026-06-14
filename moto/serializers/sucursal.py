from rest_framework import serializers
from moto.models import Sucursal


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['id', 'nombre', 'direccion', 'ciudad', 'telefono']

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_ciudad(self, value):
        if not value.strip():
            raise serializers.ValidationError("La ciudad no puede estar vacía.")
        return value
