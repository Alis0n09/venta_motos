from django.db import models
from .staff import Staff
from .sucursal import Sucursal


class SucursalStaff(models.Model):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='asignaciones_sucursal'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='staff_asignado'
    )
    fecha_asignacion = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "sucursal_staff"
        verbose_name = "Asignación de Staff a Sucursal"
        verbose_name_plural = "Asignaciones de Staff a Sucursal"
        unique_together = ('staff', 'sucursal')

    def __str__(self):
        return f"{self.staff} en {self.sucursal}"