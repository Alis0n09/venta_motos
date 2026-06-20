from rest_framework import serializers
from moto.models import SucursalStaff


class SucursalStaffSerializer(serializers.ModelSerializer):
    staff_nombre = serializers.SerializerMethodField()
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = SucursalStaff
        fields = [
            'id',
            'staff',
            'staff_nombre',
            'sucursal',
            'sucursal_nombre',
            'fecha_asignacion',
        ]
        read_only_fields = ['fecha_asignacion']

    def get_staff_nombre(self, obj):
        return f"{obj.staff.usuario.first_name} {obj.staff.usuario.last_name}"