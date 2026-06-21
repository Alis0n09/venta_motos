from django.db import models


class Compra(models.Model):
    proveedor        = models.ForeignKey('moto.Proveedor', on_delete=models.PROTECT, related_name='compras')
    sucursal_destino = models.ForeignKey('moto.Sucursal',  on_delete=models.PROTECT, related_name='compras')
    fecha            = models.DateField(auto_now_add=True)
    total            = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.empresa}"
