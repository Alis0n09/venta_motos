from rest_framework import serializers
from moto.models import Marca


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'pais_origen', 'activa']