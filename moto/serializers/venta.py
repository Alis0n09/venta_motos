from rest_framework import serializers
from moto.models import Venta, DetalleVenta, Cliente
from moto.serializers.detalle_venta import DetalleVentaSerializer


class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre  = serializers.SerializerMethodField()
    vendedor_nombre = serializers.SerializerMethodField()
    detalles        = DetalleVentaSerializer(many=True, read_only=True)
    metodo_pago     = serializers.CharField(required=False, default="efectivo")

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
            'detalles',
        ]
        read_only_fields = ['fecha_venta', 'total']

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None

    def get_vendedor_nombre(self, obj):
        if obj.vendedor:
            return f"{obj.vendedor.usuario.first_name} {obj.vendedor.usuario.last_name}"
        return None


class CrearVentaSerializer(serializers.Serializer):
    """
    Serializer para que un cliente cree su propia venta desde el frontend.
    Recibe los items del carrito y crea la Venta + DetalleVenta en un solo paso.
    """
    metodo_pago = serializers.ChoiceField(
        choices=['efectivo', 'transferencia', 'tarjeta', 'credito'],
        default='efectivo'
    )
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )

    def validate_items(self, items):
        from moto.models import Moto
        errores = []

        for i, item in enumerate(items):
            if 'moto_id' not in item:
                errores.append(f"Item {i+1}: falta moto_id.")
                continue
            if 'cantidad' not in item:
                errores.append(f"Item {i+1}: falta cantidad.")
                continue

            try:
                moto = Moto.objects.get(id=item['moto_id'])
            except Moto.DoesNotExist:
                errores.append(f"Item {i+1}: moto con id {item['moto_id']} no existe.")
                continue

            cantidad = int(item['cantidad'])
            if cantidad <= 0:
                errores.append(f"Item {i+1}: la cantidad debe ser mayor a 0.")
            elif cantidad > moto.stock:
                errores.append(
                    f"Item {i+1}: stock insuficiente para {moto.marca.nombre} {moto.modelo} "
                    f"(disponible: {moto.stock}, pedido: {cantidad})."
                )

        if errores:
            raise serializers.ValidationError(errores)

        return items

    def create(self, validated_data):
        from moto.models import Moto
        request = self.context['request']
        cliente = request.user.perfil_cliente

        items = validated_data['items']
        metodo_pago = validated_data['metodo_pago']

        total = sum(
            Moto.objects.get(id=item['moto_id']).precio * int(item['cantidad'])
            for item in items
        )

        venta = Venta.objects.create(
            cliente=cliente,
            vendedor=None,
            metodo_pago=metodo_pago,
            total=total,
        )

        for item in items:
            moto = Moto.objects.get(id=item['moto_id'])
            DetalleVenta.objects.create(
                venta=venta,
                moto=moto,
                cantidad=int(item['cantidad']),
                precio_unitario=moto.precio,
            )

        return venta