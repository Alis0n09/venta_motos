from rest_framework import serializers
from moto.models import Posventa
from moto.serializers.venta import VentaSerializer


class PosventaSerializer(serializers.ModelSerializer):
    venta_detalle = VentaSerializer(source='venta', read_only=True)

    class Meta:
        model = Posventa
        fields = [
            'id', 'venta', 'venta_detalle', 'fecha_apertura',
            'fecha_cierre', 'estado', 'observaciones'
        ]
        read_only_fields = ['fecha_apertura']
