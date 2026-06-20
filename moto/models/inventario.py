from django.db import models
from .moto import Moto
from .sucursal import Sucursal


class Inventario(models.Model):
    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='inventarios'
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name='inventarios'
    )
    cantidad = models.PositiveIntegerField(default=0)
    ubicacion_bodega = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "inventario"
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        unique_together = ('moto', 'sucursal')

    def __str__(self):
        return f"{self.moto} en {self.sucursal} ({self.cantidad})"