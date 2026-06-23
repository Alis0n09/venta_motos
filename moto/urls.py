# moto/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from moto.views.health          import health_check, testing_cicd
from moto.views.auth            import RegisterView, LogoutView
from moto.views.user            import UserViewSet
from moto.views.cliente         import ClienteViewSet
from moto.views.vendedor        import VendedorViewSet
from moto.views.moto            import MotoViewSet
from moto.views.venta           import VentaViewSet
from moto.views.detalle_venta   import DetalleVentaViewSet
from moto.views.sucursal        import SucursalViewSet
from moto.views.direccion       import DireccionViewSet
from moto.views.proveedor       import ProveedorViewSet
from moto.views.garantia        import GarantiaViewSet
from moto.views.mantenimiento   import MantenimientoViewSet
from moto.views.categoria       import CategoriaViewSet
from moto.views.marca           import MarcaViewSet
from moto.views.repuesto        import RepuestoViewSet
from moto.views.inventario      import InventarioViewSet
from moto.views.sucursal_staff  import SucursalStaffViewSet
from moto.views.compra          import CompraViewSet
from moto.views.detalle_compra  import DetalleCompraViewSet
from moto.views.financiamiento  import FinanciamientoViewSet
from moto.views.cuota_pago      import CuotaPagoViewSet
from moto.views.historial_precio import HistorialPrecioViewSet
from moto.views.resena          import ResenaViewSet
from moto.views.logs_actividad  import LogsActividadViewSet
from moto.serializers.auth      import CustomTokenView


router = DefaultRouter()
router.register('users',             UserViewSet,            basename='user')
router.register('clientes',          ClienteViewSet,         basename='cliente')
router.register('vendedores',        VendedorViewSet,        basename='vendedor')
router.register('motos',             MotoViewSet,            basename='moto')
router.register('ventas',            VentaViewSet,           basename='venta')
router.register('detalle-ventas',    DetalleVentaViewSet,    basename='detalle-venta')
router.register('sucursales',        SucursalViewSet,        basename='sucursal')
router.register('direcciones',       DireccionViewSet,       basename='direccion')
router.register('proveedores',       ProveedorViewSet,       basename='proveedor')
router.register('garantias',         GarantiaViewSet,        basename='garantia')
router.register('mantenimientos',    MantenimientoViewSet,   basename='mantenimiento')
router.register('categorias',        CategoriaViewSet,       basename='categoria')
router.register('marcas',            MarcaViewSet,           basename='marca')
router.register('repuestos',         RepuestoViewSet,        basename='repuesto')
router.register('inventario',        InventarioViewSet,      basename='inventario')
router.register('sucursal-staff',    SucursalStaffViewSet,   basename='sucursal-staff')
router.register('compras',           CompraViewSet,          basename='compra')
router.register('detalle-compras',   DetalleCompraViewSet,   basename='detalle-compra')
router.register('financiamientos',   FinanciamientoViewSet,  basename='financiamiento')
router.register('cuotas-pago',       CuotaPagoViewSet,       basename='cuota-pago')
router.register('historial-precios', HistorialPrecioViewSet, basename='historial-precio')
router.register('resenas',           ResenaViewSet,          basename='resena')
router.register('logs-actividad',    LogsActividadViewSet,   basename='logs-actividad')


urlpatterns = [
    path('health/',             health_check),
    path('testing-cicd/',       testing_cicd),

    path('auth/register/',      RegisterView.as_view()),
    path('auth/login/',         CustomTokenView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/token/verify/',  TokenVerifyView.as_view()),
    path('auth/logout/',        LogoutView.as_view()),

    path('', include(router.urls)),
]
