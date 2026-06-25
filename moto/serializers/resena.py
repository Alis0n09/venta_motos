from rest_framework import serializers
from moto.models import Resena, Cliente


class ResenaSerializer(serializers.ModelSerializer):
    moto_nombre    = serializers.SerializerMethodField()
    cliente_nombre = serializers.SerializerMethodField()
    cliente        = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Resena
        fields = [
            'id',
            'moto',
            'moto_nombre',
            'cliente',
            'cliente_nombre',
            'rating',
            'comentario',
            'fecha',
        ]
        read_only_fields = ['fecha']

    def get_moto_nombre(self, obj):
        if obj.moto and obj.moto.marca:
            return f"{obj.moto.marca.nombre} {obj.moto.modelo}"
        return obj.moto.modelo if obj.moto else None

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("El rating debe estar entre 1 y 5.")
        return value