from django.db import models
from .cliente import Cliente


class HistorialCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    tipo_evento = models.CharField(max_length=100)
    detalle = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "historial_cliente"
        verbose_name = "Historial de Cliente"
        verbose_name_plural = "Historiales de Clientes"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.cliente} - {self.tipo_evento} ({self.fecha})"
