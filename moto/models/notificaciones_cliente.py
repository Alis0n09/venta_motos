from django.db import models
from .cliente import Cliente


class NotificacionesCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=50)
    mensaje = models.CharField(max_length=255)
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notificaciones_cliente"
        verbose_name = "Notificación de Cliente"
        verbose_name_plural = "Notificaciones de Clientes"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.cliente} - {self.tipo}: {self.mensaje[:50]}"
