from django.db import models


class Proveedor(models.Model):
    empresa = models.CharField(max_length=150)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.empresa
