from django.db import transaction
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

    def _descontar_stock(self, moto, cantidad, venta, usuario):
        """
        Descuenta `cantidad` unidades de `moto` del inventario, empezando por la
        sucursal con más existencias y continuando con las siguientes hasta
        completar el total (o lanzando ValidationError si no alcanza).
        Deja constancia de cada ajuste en LogsActividad.
        """
        from moto.models import Inventario, LogsActividad

        pendiente = cantidad
        inventarios = Inventario.objects.select_for_update().filter(
            moto=moto
        ).order_by('-cantidad')

        for inv in inventarios:
            if pendiente <= 0:
                break
            if inv.cantidad <= 0:
                continue

            cantidad_antes = inv.cantidad
            descontado = min(inv.cantidad, pendiente)
            inv.cantidad -= descontado
            inv.save(update_fields=['cantidad'])
            pendiente -= descontado

            LogsActividad.objects.create(
                usuario=usuario,
                accion='UPDATE',
                entidad='Inventario',
                datos_antes={
                    'id': inv.id,
                    'moto': moto.id,
                    'sucursal': inv.sucursal_id,
                    'cantidad': cantidad_antes,
                },
                datos_despues={
                    'id': inv.id,
                    'moto': moto.id,
                    'sucursal': inv.sucursal_id,
                    'cantidad': inv.cantidad,
                    'descontado': descontado,
                    'venta_id': venta.id,
                },
            )

        if pendiente > 0:
            raise serializers.ValidationError(
                f"Stock insuficiente para {moto.marca.nombre} {moto.modelo}: "
                f"faltaron {pendiente} unidad(es) por descontar de inventario "
                f"(posiblemente otra compra se adelantó)."
            )

    def create(self, validated_data):
        from moto.models import Moto, HistorialCliente
        request = self.context['request']
        cliente = request.user.perfil_cliente

        items = validated_data['items']
        metodo_pago = validated_data['metodo_pago']

        total = sum(
            Moto.objects.get(id=item['moto_id']).precio * int(item['cantidad'])
            for item in items
        )

        with transaction.atomic():
            venta = Venta.objects.create(
                cliente=cliente,
                vendedor=None,
                metodo_pago=metodo_pago,
                total=total,
            )

            motos_compradas = []
            for item in items:
                moto = Moto.objects.get(id=item['moto_id'])
                cantidad = int(item['cantidad'])
                DetalleVenta.objects.create(
                    venta=venta,
                    moto=moto,
                    cantidad=cantidad,
                    precio_unitario=moto.precio,
                )
                self._descontar_stock(moto, cantidad, venta, request.user)
                if moto.marca:
                    motos_compradas.append(f"{moto.marca.nombre} {moto.modelo} ({moto.anio})")

            # Registrar historial del cliente
            HistorialCliente.objects.create(
                cliente=cliente,
                tipo_evento='compra',
                detalle={
                    'venta_id': venta.id,
                    'total': str(venta.total),
                    'metodo_pago': venta.metodo_pago,
                    'motos': motos_compradas,
                }
            )

        return venta