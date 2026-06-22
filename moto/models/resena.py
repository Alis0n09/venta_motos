from django.db import models
from .moto import Moto
from .cliente import Cliente


class Resena(models.Model):
    moto = models.ForeignKey(
        Moto,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    rating = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resenas"
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha']
        unique_together = ('moto', 'cliente')

    def __str__(self):
        return f"{self.cliente} → {self.moto} ({self.rating}★)"