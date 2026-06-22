from django.db import models
from .venta import Venta


def _add_months(source, months):
    month = source.month - 1 + months
    year = source.year + month // 12
    month = month % 12 + 1
    import calendar
    _, last_day = calendar.monthrange(year, month)
    day = min(source.day, last_day)
    return source.replace(year=year, month=month, day=day)


class Financiamiento(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]

    venta = models.OneToOneField(
        Venta,
        on_delete=models.CASCADE,
        related_name='financiamiento'
    )
    monto_financiado = models.DecimalField(max_digits=10, decimal_places=2)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)
    plazo_meses = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo'
    )

    class Meta:
        db_table = "financiamientos"
        verbose_name = "Financiamiento"
        verbose_name_plural = "Financiamientos"

    def __str__(self):
        return f"Financiamiento #{self.id} - Venta #{self.venta_id}"

    def save(self, *args, **kwargs):
        if not self.fecha_fin and self.fecha_inicio and self.plazo_meses:
            self.fecha_fin = _add_months(self.fecha_inicio, self.plazo_meses)
        super().save(*args, **kwargs)
