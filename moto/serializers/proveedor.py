from rest_framework import serializers
from moto.models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'empresa', 'contacto', 'correo', 'pais']

    def validate_empresa(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre de la empresa no puede estar vacío.")
        return value

    def validate_correo(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError("Ingrese una dirección de correo electrónico válida.")
        return value
