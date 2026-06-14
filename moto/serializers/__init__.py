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
