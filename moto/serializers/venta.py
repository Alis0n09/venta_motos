from rest_framework import serializers
from moto.models import Venta


class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    vendedor_nombre = serializers.SerializerMethodField()

    metodo_pago = serializers.CharField(required=False, default="efectivo")

    class Meta:
        model = Venta
        fields = [
            'id',
            'cliente',
            'vendedor',
            'fecha_venta',
            'metodo_pago',
            'total',
            'cliente_nombre',
            'vendedor_nombre',
        ]
        read_only_fields = ['fecha_venta']

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None

    def get_vendedor_nombre(self, obj):
        if obj.vendedor:
            return f"{obj.vendedor.usuario.first_name} {obj.vendedor.usuario.last_name}"
        return None

    def validate_total(self, value):
        if value < 0:
            raise serializers.ValidationError("El total no puede ser negativo.")
        return value