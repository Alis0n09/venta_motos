# moto/models/favorito.py

from django.db import models
from .cliente import Cliente
from .moto import Moto


class Favorito(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='favoritos'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favoritos'
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        ordering = ['-fecha']
        # Un cliente no puede marcar la misma moto como favorita dos veces.
        unique_together = ('cliente', 'moto')

    def __str__(self):
        return f"{self.cliente} - {self.moto}"