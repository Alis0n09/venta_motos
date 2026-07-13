# moto/serializers/favorito.py

from rest_framework import serializers
from moto.models import Favorito


class FavoritoSerializer(serializers.ModelSerializer):
    moto_nombre = serializers.SerializerMethodField()
    moto_precio = serializers.SerializerMethodField()
    moto_estado = serializers.SerializerMethodField()
    moto_imagen_url = serializers.SerializerMethodField()
    moto_stock = serializers.SerializerMethodField()

    class Meta:
        model = Favorito
        fields = [
            'id',
            'cliente',
            'moto',
            'moto_nombre',
            'moto_precio',
            'moto_estado',
            'moto_imagen_url',
            'moto_stock',
            'fecha',
        ]
        read_only_fields = ['cliente', 'fecha']

    def get_moto_nombre(self, obj):
        if obj.moto and obj.moto.marca:
            return f"{obj.moto.marca.nombre} {obj.moto.modelo}"
        return obj.moto.modelo if obj.moto else None

    def get_moto_precio(self, obj):
        return str(obj.moto.precio) if obj.moto else None

    def get_moto_estado(self, obj):
        return obj.moto.estado if obj.moto else None

    def get_moto_imagen_url(self, obj):
        return obj.moto.imagen_url if obj.moto else None

    def get_moto_stock(self, obj):
        return obj.moto.stock if obj.moto else None