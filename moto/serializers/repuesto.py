from rest_framework import serializers
from moto.models import Repuesto


class RepuestoSerializer(serializers.ModelSerializer):
    marca_compatible_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Repuesto
        fields = [
            'id',
            'nombre',
            'marca_compatible',
            'marca_compatible_nombre',
            'stock',
            'precio',
        ]

    def get_marca_compatible_nombre(self, obj):
        if obj.marca_compatible:
            return obj.marca_compatible.nombre
        return None

    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value