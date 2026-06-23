from django.conf import settings
from django.db import models


class LogsActividad(models.Model):
    usuario      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs',
    )
    accion        = models.CharField(max_length=100)
    entidad       = models.CharField(max_length=100)
    datos_antes   = models.JSONField(null=True, blank=True)
    datos_despues = models.JSONField(null=True, blank=True)
    fecha         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accion} - {self.entidad} ({self.fecha})"
