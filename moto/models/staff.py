from django.conf import settings
from django.db import models


class Staff(models.Model):

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        VENDEDOR = "vendedor", "Vendedor"
        BODEGUERO = "bodeguero", "Bodeguero"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_staff'
    )
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.VENDEDOR)

    class Meta:
        db_table = "staff"
        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.rol})"