from django.db import models
from .posventa import Posventa


class Garantia(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('expirada', 'Expirada'),
        ('cancelada', 'Cancelada'),
    ]

    posventa = models.ForeignKey(
        Posventa,
        on_delete=models.CASCADE,
        related_name='garantias'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_cobertura = models.CharField(max_length=100)
    detalles = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activa'
    )

    class Meta:
        db_table = "garantias"
        verbose_name = "Garantía"
        verbose_name_plural = "Garantías"

    def __str__(self):
        return f"Garantía #{self.id} - {self.tipo_cobertura}"
