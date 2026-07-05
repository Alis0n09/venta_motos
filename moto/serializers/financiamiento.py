from rest_framework import serializers
from moto.models import Financiamiento


class FinanciamientoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    cliente_cedula = serializers.SerializerMethodField()
    moto_detalle   = serializers.SerializerMethodField()
    cuota_mensual  = serializers.SerializerMethodField()

    class Meta:
        model = Financiamiento
        fields = [
            'id',
            'venta',
            'cliente_nombre',
            'cliente_cedula',
            'moto_detalle',
            'monto_financiado',
            'tasa_interes',
            'plazo_meses',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'cuota_mensual',
        ]
        read_only_fields = ['id', 'fecha_fin']

    def get_cliente_nombre(self, obj):
        if obj.venta and obj.venta.cliente:
            c = obj.venta.cliente
            return f"{c.nombre} {c.apellido}"
        return None

    def get_cliente_cedula(self, obj):
        if obj.venta and obj.venta.cliente:
            return obj.venta.cliente.cedula
        return None

    def get_moto_detalle(self, obj):
        if obj.venta:
            detalles = obj.venta.detalles.select_related('moto__marca').all()
            return [
                f"{d.moto.marca.nombre} {d.moto.modelo} ({d.moto.anio})"
                for d in detalles
            ]
        return []

    def get_cuota_mensual(self, obj):
        """Cuota mensual calculada por el modelo (sistema francés)."""
        cuota = obj.calcular_cuota_mensual()
        return float(cuota) if cuota is not None else None

    def validate_monto_financiado(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto financiado debe ser mayor a cero.")
        return value

    def validate_tasa_interes(self, value):
        if value < 0:
            raise serializers.ValidationError("La tasa de interés no puede ser negativa.")
        return value

    def validate(self, data):
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return data