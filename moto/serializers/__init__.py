from moto.serializers.auth import CustomTokenSerializer, CustomTokenView

from moto.serializers.user import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

from moto.serializers.cliente import ClienteSerializer
from moto.serializers.vendedor import VendedorSerializer
from moto.serializers.moto import MotoSerializer
from moto.serializers.venta import VentaSerializer
from moto.serializers.detalle_venta import DetalleVentaSerializer
from moto.serializers.sucursal import SucursalSerializer
from moto.serializers.direccion import DireccionSerializer
from moto.serializers.proveedor import ProveedorSerializer
from moto.serializers.posventa import PosventaSerializer
from moto.serializers.garantia import GarantiaSerializer
from moto.serializers.mantenimiento import MantenimientoSerializer
from moto.serializers.categoria import CategoriaSerializer
from moto.serializers.marca import MarcaSerializer
from moto.serializers.repuesto import RepuestoSerializer
from moto.serializers.inventario import InventarioSerializer
from moto.serializers.sucursal_staff import SucursalStaffSerializer
from moto.serializers.compra import CompraSerializer
from moto.serializers.detalle_compra import DetalleCompraSerializer
from moto.serializers.financiamiento import FinanciamientoSerializer
from moto.serializers.cuota_pago import CuotaPagoSerializer
from moto.serializers.historial_precio import HistorialPrecioSerializer
from moto.serializers.resena import ResenaSerializer
