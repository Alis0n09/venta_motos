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
from moto.serializers.marca import MarcaSerializer
from moto.serializers.categoria import CategoriaSerializer
from moto.serializers.repuesto import RepuestoSerializer