from django.db import models
from .venta import Venta


class Garantia(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='garantias'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo = models.CharField(max_length=50)

    class Meta:
        db_table = "garantias"
        verbose_name = "Garantía"
        verbose_name_plural = "Garantías"

    def __str__(self):
        return f"Garantía #{self.id} - Venta #{self.venta_id}"
