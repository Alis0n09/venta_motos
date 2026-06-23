from rest_framework import serializers
from moto.models import Mantenimiento


class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'
        read_only_fields = ['id']

    def validate_costo(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value
