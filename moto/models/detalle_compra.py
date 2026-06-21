from django.db import models


class DetalleCompra(models.Model):
    compra       = models.ForeignKey('moto.Compra', on_delete=models.CASCADE, related_name='detalles')
    moto         = models.ForeignKey('moto.Moto',   on_delete=models.PROTECT, related_name='detalles_compra')
    cantidad     = models.PositiveIntegerField(default=1)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.moto} x{self.cantidad}"
