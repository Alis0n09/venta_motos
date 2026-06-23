from django.db import models
from .cliente import Cliente
from .staff import Staff


class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('credito', 'Crédito'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    vendedor = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name='ventas_realizadas',
        null=True,
        blank=True
    )
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(
        max_length=50,
        choices=METODO_PAGO_CHOICES
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"