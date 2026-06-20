from rest_framework import serializers
from moto.models import Inventario


class InventarioSerializer(serializers.ModelSerializer):
    moto_nombre = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = [
            'id',
            'moto',
            'moto_nombre',
            'sucursal',
            'sucursal_nombre',
            'cantidad',
            'ubicacion_bodega',
        ]

    def get_moto_nombre(self, obj):
        return f"{obj.moto.marca.nombre} {obj.moto.modelo}" if obj.moto.marca else obj.moto.modelo

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value