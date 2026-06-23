from django.db import models
from .financiamiento import Financiamiento


class CuotaPago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]

    financiamiento = models.ForeignKey(
        Financiamiento,
        on_delete=models.CASCADE,
        related_name='cuotas'
    )
    numero_cuota = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    class Meta:
        db_table = "cuotas_pago"
        verbose_name = "Cuota de Pago"
        verbose_name_plural = "Cuotas de Pago"
        ordering = ['financiamiento', 'numero_cuota']
        constraints = [
            models.UniqueConstraint(
                fields=['financiamiento', 'numero_cuota'],
                name='unique_cuota_por_financiamiento'
            ),
        ]

    def __str__(self):
        return f"Cuota #{self.numero_cuota} - Financiamiento #{self.financiamiento_id}"
