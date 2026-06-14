from rest_framework import serializers
from moto.models import Direccion


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['id', 'cliente', 'calle', 'ciudad', 'provincia', 'principal']

    def validate_calle(self, value):
        if not value.strip():
            raise serializers.ValidationError("La calle no puede estar vacía.")
        return value

    def validate_ciudad(self, value):
        if not value.strip():
            raise serializers.ValidationError("La ciudad no puede estar vacía.")
        return value
