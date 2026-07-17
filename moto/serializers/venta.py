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
    # ── Financiamiento parcial opcional ──────────────────────────────────────
    # Si el cliente quiere financiar parte de la compra, envía estos 2 campos
    # juntos (el resto de la compra la paga con `metodo_pago`). El cliente NO
    # elige la tasa de interés: la fija un admin al aprobar la solicitud
    # (ver FinanciamientoViewSet.aprobar). Si no envía estos campos, el
    # comportamiento es idéntico al de siempre (venta 100% al contado).
    monto_a_financiar = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, default=None
    )
    plazo_meses = serializers.IntegerField(required=False, allow_null=True, default=None)

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

    def validate(self, data):
        """Valida el financiamiento parcial opcional, sin afectar la
        validación normal de items/metodo_pago si no se está financiando."""
        monto = data.get('monto_a_financiar')
        plazo = data.get('plazo_meses')

        campos = [monto, plazo]
        algunos = any(c is not None for c in campos)
        todos = all(c is not None for c in campos)

        if algunos and not todos:
            raise serializers.ValidationError(
                "Para financiar parte de la compra debes enviar "
                "monto_a_financiar y plazo_meses juntos."
            )

        if todos:
            from moto.models import Moto

            if monto <= 0:
                raise serializers.ValidationError({"monto_a_financiar": "Debe ser mayor a cero."})
            if plazo <= 0:
                raise serializers.ValidationError({"plazo_meses": "Debe ser mayor a cero."})

            total_items = sum(
                Moto.objects.get(id=item['moto_id']).precio * int(item['cantidad'])
                for item in data['items']
            )
            if monto > total_items:
                raise serializers.ValidationError(
                    {"monto_a_financiar": "No puede ser mayor al total de la compra."}
                )

        return data

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
        from datetime import date
        from moto.models import Moto, HistorialCliente, Financiamiento
        request = self.context['request']
        cliente = request.user.perfil_cliente

        items = validated_data['items']
        metodo_pago = validated_data['metodo_pago']
        monto_a_financiar = validated_data.get('monto_a_financiar')
        plazo_meses = validated_data.get('plazo_meses')

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

            financiamiento_creado = None
            if monto_a_financiar:
                # Queda 'pendiente' y SIN tasa de interés todavía: un admin
                # debe fijar la tasa y aprobar (o rechazar) la solicitud desde
                # el panel. El signal generar_cuotas_financiamiento (ya
                # existente en el backend) arma el plan de cuotas recién
                # cuando el admin aprueba (pendiente -> activo).
                financiamiento_creado = Financiamiento.objects.create(
                    venta=venta,
                    monto_financiado=monto_a_financiar,
                    tasa_interes=None,
                    plazo_meses=plazo_meses,
                    fecha_inicio=date.today(),
                    estado='pendiente',
                )

            # Registrar historial del cliente
            detalle_historial = {
                'venta_id': venta.id,
                'total': str(venta.total),
                'metodo_pago': venta.metodo_pago,
                'motos': motos_compradas,
            }
            if financiamiento_creado:
                detalle_historial['monto_financiado'] = str(financiamiento_creado.monto_financiado)
                detalle_historial['monto_contado'] = str(venta.total - financiamiento_creado.monto_financiado)

            HistorialCliente.objects.create(
                cliente=cliente,
                tipo_evento='compra',
                detalle=detalle_historial,
            )

        return venta