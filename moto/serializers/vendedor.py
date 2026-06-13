# moto/serializers/vendedor.py

from rest_framework import serializers
from moto.models import Staff, Usuario


class VendedorSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    nombre = serializers.CharField(source='usuario.first_name', read_only=True)
    apellido = serializers.CharField(source='usuario.last_name', read_only=True)
    cedula = serializers.CharField(source='usuario.cedula', read_only=True)
    telefono = serializers.CharField(source='usuario.telefono', read_only=True)
    correo = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id',
            'usuario',
            'nombre',
            'apellido',
            'cedula',
            'telefono',
            'correo',
            'rol',
        ]