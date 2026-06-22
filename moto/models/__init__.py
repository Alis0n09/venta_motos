# moto/models/__init__.py

from .cliente import Cliente
from .staff import Staff
from .usuario import Usuario
from .moto import Moto
from .venta import Venta
from .detalle_venta import DetalleVenta
from .sucursal import Sucursal
from .direccion import Direccion
from .proveedor import Proveedor
from .posventa import Posventa
from .garantia import Garantia
from .mantenimiento import Mantenimiento
from .categoria import Categoria
from .marca import Marca
from .repuesto import Repuesto
from .inventario import Inventario
from .sucursal_staff import SucursalStaff
from .compra import Compra
from .detalle_compra import DetalleCompra
from .historial_precio import HistorialPrecio
from .resena import Resena

__all__ = [
    'Cliente',
    'Staff',
    'Usuario',
    'Moto',
    'Venta',
    'DetalleVenta',
    'Sucursal',
    'Direccion',
    'Proveedor',
    'Posventa',
    'Garantia',
    'Mantenimiento',
    'Categoria',
    'Marca',
    'Repuesto',
    'Inventario',
    'SucursalStaff',
    'Compra',
    'DetalleCompra',
    'HistorialPrecio',
    'Resena',
]