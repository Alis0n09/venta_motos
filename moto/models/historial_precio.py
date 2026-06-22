from django.db import models
from .moto import Moto
from .usuario import Usuario


class HistorialPrecio(models.Model):
    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='historial_precios'
    )
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cambios_precio'
    )

    class Meta:
        db_table = "historial_precios"
        verbose_name = "Historial de Precio"
        verbose_name_plural = "Historial de Precios"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.moto} | {self.precio_anterior} → {self.precio_nuevo}"