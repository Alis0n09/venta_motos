from django.db import models


class Direccion(models.Model):
    cliente = models.ForeignKey(
        'moto.Cliente',
        on_delete=models.CASCADE,
        related_name='direcciones'
    )
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"
