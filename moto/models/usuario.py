from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    cedula = models.CharField(max_length=10, blank=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"