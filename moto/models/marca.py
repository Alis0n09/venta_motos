from django.db import models


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    pais_origen = models.CharField(max_length=100, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "marcas"
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre