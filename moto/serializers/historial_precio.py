from rest_framework import serializers
from moto.models import HistorialPrecio


class HistorialPrecioSerializer(serializers.ModelSerializer):
    moto_nombre = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialPrecio
        fields = [
            'id',
            'moto',
            'moto_nombre',
            'precio_anterior',
            'precio_nuevo',
            'fecha',
            'usuario',
            'usuario_nombre',
        ]
        read_only_fields = ['fecha']

    def get_moto_nombre(self, obj):
        if obj.moto and obj.moto.marca:
            return f"{obj.moto.marca.nombre} {obj.moto.modelo}"
        return obj.moto.modelo if obj.moto else None

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f"{obj.usuario.first_name} {obj.usuario.last_name}"
        return None

    def validate(self, data):
        if data.get('precio_anterior') == data.get('precio_nuevo'):
            raise serializers.ValidationError(
                "El precio nuevo debe ser diferente al precio anterior."
            )
        if data.get('precio_nuevo') <= 0:
            raise serializers.ValidationError(
                "El precio nuevo debe ser mayor a 0."
            )
        return data