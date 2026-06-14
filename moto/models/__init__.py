# moto/models/__init__.py

from .cliente import Cliente
from .staff import Staff
from .usuario import Usuario
from .moto import Moto
from .venta import Venta
from .detalle_venta import DetalleVenta
from .marca import Marca
from .categoria import Categoria
from .repuesto import Repuesto

__all__ = [
    'Cliente',
    'Staff',
    'Usuario',
    'Moto',
    'Venta',
    'DetalleVenta',
    'Marca',
    'Categoria',
    'Repuesto',
]