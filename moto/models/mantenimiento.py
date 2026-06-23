from django.db import models
from .moto import Moto
from .cliente import Cliente


class Mantenimiento(models.Model):
    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    fecha = models.DateField()
    tipo = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "mantenimientos"
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"

    def __str__(self):
        return f"Mantenimiento #{self.id} - {self.tipo}"
