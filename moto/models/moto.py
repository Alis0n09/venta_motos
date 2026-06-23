from django.db import models
from .marca import Marca
from .categoria import Categoria


class Moto(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendida', 'Vendida'),
        ('reservada', 'Reservada'),
    ]

    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='motos'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='motos'
    )
    modelo = models.CharField(max_length=100)
    anio = models.IntegerField()
    cilindraje = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible'
    )

    @property
    def stock(self):
        return sum(i.cantidad for i in self.inventarios.all())

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.anio}"