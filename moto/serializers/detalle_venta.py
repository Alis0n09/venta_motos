from rest_framework import serializers
from moto.models import DetalleVenta


class DetalleVentaSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    moto_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'venta',
            'moto',
            'moto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]

    def get_subtotal(self, obj):
        return obj.cantidad * obj.precio_unitario

    def get_moto_nombre(self, obj):
        if obj.moto and obj.moto.marca:
            return f"{obj.moto.marca.nombre} {obj.moto.modelo}"
        return obj.moto.modelo if obj.moto else None

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def validate_precio_unitario(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio unitario debe ser mayor a 0.")
        return value

    def validate(self, data):
        moto = data.get('moto')
        cantidad = data.get('cantidad')

        if moto and cantidad:
            stock_disponible = moto.stock
            if stock_disponible > 0 and cantidad > stock_disponible:
                raise serializers.ValidationError({
                    "cantidad": f"La cantidad no puede ser mayor al stock disponible ({stock_disponible})."
                })

        return data