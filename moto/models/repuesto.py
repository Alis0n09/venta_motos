from django.db import models
from .marca import Marca


class Repuesto(models.Model):
    nombre = models.CharField(max_length=100)
    marca_compatible = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repuestos'
    )
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "repuestos"
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"

    def __str__(self):
        return self.nombre