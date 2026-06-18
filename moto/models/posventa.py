from django.db import models
from .venta import Venta


class Posventa(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    venta = models.OneToOneField(
        Venta,
        on_delete=models.CASCADE,
        related_name='posventa'
    )
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "posventas"
        verbose_name = "Posventa"
        verbose_name_plural = "Posventas"

    def __str__(self):
        return f"Posventa #{self.id} - Venta #{self.venta_id}"
