from django.db import models
from .posventa import Posventa
from .moto import Moto


class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    posventa = models.ForeignKey(
        Posventa,
        on_delete=models.CASCADE,
        related_name='mantenimientos'
    )
    moto = models.ForeignKey(
        Moto,
        on_delete=models.PROTECT,
        related_name='mantenimientos'
    )
    tipo_mantenimiento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )
    fecha_programada = models.DateField()
    fecha_realizacion = models.DateField(null=True, blank=True)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "mantenimientos"
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"

    def __str__(self):
        return f"Mantenimiento #{self.id} - {self.tipo_mantenimiento}"
