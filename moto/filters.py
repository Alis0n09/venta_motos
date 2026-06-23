# moto/filters.py

import django_filters
from moto.models import (
    Cliente, Staff, Moto, Venta, DetalleVenta,
    Sucursal, Direccion, Proveedor,
    Garantia, Mantenimiento,
    Categoria, Marca, Repuesto,
    Inventario, SucursalStaff,
    Compra, DetalleCompra,
    Financiamiento, CuotaPago,
    HistorialPrecio, Resena,
    LogsActividad,
)


class ClienteFilter(django_filters.FilterSet):
    nombre   = django_filters.CharFilter(lookup_expr='icontains')
    apellido = django_filters.CharFilter(lookup_expr='icontains')
    cedula   = django_filters.CharFilter(lookup_expr='icontains')
    email    = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = Cliente
        fields = ['cedula', 'email']


class VendedorFilter(django_filters.FilterSet):
    nombre   = django_filters.CharFilter(field_name='usuario__first_name', lookup_expr='icontains')
    apellido = django_filters.CharFilter(field_name='usuario__last_name', lookup_expr='icontains')
    cedula   = django_filters.CharFilter(field_name='usuario__cedula', lookup_expr='icontains')
    correo   = django_filters.CharFilter(field_name='usuario__email', lookup_expr='icontains')
    telefono = django_filters.CharFilter(field_name='usuario__telefono', lookup_expr='icontains')
    rol      = django_filters.CharFilter(field_name='rol', lookup_expr='icontains')

    class Meta:
        model = Staff
        fields = ['rol']


class MotoFilter(django_filters.FilterSet):
    marca        = django_filters.NumberFilter(field_name='marca_id')
    marca_nombre = django_filters.CharFilter(field_name='marca__nombre', lookup_expr='icontains')
    categoria    = django_filters.NumberFilter(field_name='categoria_id')
    modelo       = django_filters.CharFilter(lookup_expr='icontains')
    color        = django_filters.CharFilter(lookup_expr='icontains')
    precio_min   = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max   = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    stock_min    = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max    = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    anio_min     = django_filters.NumberFilter(field_name='anio', lookup_expr='gte')
    anio_max     = django_filters.NumberFilter(field_name='anio', lookup_expr='lte')

    class Meta:
        model  = Moto
        fields = ['marca', 'categoria', 'modelo', 'anio', 'color']


class VentaFilter(django_filters.FilterSet):
    cliente = django_filters.NumberFilter(field_name='cliente_id')
    vendedor = django_filters.NumberFilter(field_name='vendedor_id')
    total = django_filters.NumberFilter(field_name='total')
    metodo_pago = django_filters.CharFilter(field_name='metodo_pago', lookup_expr='icontains')
    fecha_venta = django_filters.DateFilter(field_name='fecha_venta')

    class Meta:
        model = Venta
        fields = ['cliente', 'vendedor', 'total', 'metodo_pago', 'fecha_venta']


class DetalleVentaFilter(django_filters.FilterSet):
    cantidad_min        = django_filters.NumberFilter(field_name='cantidad', lookup_expr='gte')
    cantidad_max        = django_filters.NumberFilter(field_name='cantidad', lookup_expr='lte')
    precio_unitario_min = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='gte')
    precio_unitario_max = django_filters.NumberFilter(field_name='precio_unitario', lookup_expr='lte')
    moto_marca          = django_filters.CharFilter(field_name='moto__marca__nombre', lookup_expr='icontains')
    moto_modelo         = django_filters.CharFilter(field_name='moto__modelo', lookup_expr='icontains')

    class Meta:
        model  = DetalleVenta
        fields = ['venta', 'moto', 'cantidad', 'precio_unitario']


class SucursalFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    ciudad = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = Sucursal
        fields = ['nombre', 'ciudad']


class DireccionFilter(django_filters.FilterSet):
    cliente   = django_filters.NumberFilter(field_name='cliente_id')
    ciudad    = django_filters.CharFilter(lookup_expr='icontains')
    provincia = django_filters.CharFilter(lookup_expr='icontains')
    principal = django_filters.BooleanFilter()

    class Meta:
        model  = Direccion
        fields = ['cliente', 'ciudad', 'provincia', 'principal']


class ProveedorFilter(django_filters.FilterSet):
    empresa  = django_filters.CharFilter(lookup_expr='icontains')
    pais     = django_filters.CharFilter(lookup_expr='icontains')
    contacto = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = Proveedor
        fields = ['empresa', 'pais']


class GarantiaFilter(django_filters.FilterSet):
    venta = django_filters.NumberFilter(field_name='venta_id')
    tipo = django_filters.CharFilter(lookup_expr='icontains')
    fecha_inicio = django_filters.DateFilter(field_name='fecha_inicio')
    fecha_fin = django_filters.DateFilter(field_name='fecha_fin')

    class Meta:
        model = Garantia
        fields = ['venta', 'tipo', 'fecha_inicio', 'fecha_fin']


class CategoriaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class MarcaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    pais_origen = django_filters.CharFilter(lookup_expr='icontains')
    activa = django_filters.BooleanFilter()

    class Meta:
        model = Marca
        fields = ['nombre', 'pais_origen', 'activa']


class RepuestoFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    stock_min = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    marca_compatible = django_filters.NumberFilter(field_name='marca_compatible_id')

    class Meta:
        model = Repuesto
        fields = ['nombre', 'precio', 'stock', 'marca_compatible']


class MantenimientoFilter(django_filters.FilterSet):
    moto = django_filters.NumberFilter(field_name='moto_id')
    cliente = django_filters.NumberFilter(field_name='cliente_id')
    tipo = django_filters.CharFilter(lookup_expr='icontains')
    fecha = django_filters.DateFilter(field_name='fecha')
    costo_min = django_filters.NumberFilter(field_name='costo', lookup_expr='gte')
    costo_max = django_filters.NumberFilter(field_name='costo', lookup_expr='lte')

    class Meta:
        model = Mantenimiento
        fields = ['moto', 'cliente', 'tipo', 'fecha', 'costo']


class InventarioFilter(django_filters.FilterSet):
    moto         = django_filters.NumberFilter(field_name='moto_id')
    sucursal     = django_filters.NumberFilter(field_name='sucursal_id')
    cantidad_min = django_filters.NumberFilter(field_name='cantidad', lookup_expr='gte')
    cantidad_max = django_filters.NumberFilter(field_name='cantidad', lookup_expr='lte')

    class Meta:
        model  = Inventario
        fields = ['moto', 'sucursal', 'cantidad']


class SucursalStaffFilter(django_filters.FilterSet):
    staff            = django_filters.NumberFilter(field_name='staff_id')
    sucursal         = django_filters.NumberFilter(field_name='sucursal_id')
    fecha_asignacion = django_filters.DateFilter(field_name='fecha_asignacion')

    class Meta:
        model  = SucursalStaff
        fields = ['staff', 'sucursal', 'fecha_asignacion']


class CompraFilter(django_filters.FilterSet):
    proveedor        = django_filters.NumberFilter(field_name='proveedor_id')
    sucursal_destino = django_filters.NumberFilter(field_name='sucursal_destino_id')
    fecha            = django_filters.DateFilter(field_name='fecha')
    total_min        = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max        = django_filters.NumberFilter(field_name='total', lookup_expr='lte')

    class Meta:
        model  = Compra
        fields = ['proveedor', 'sucursal_destino', 'fecha', 'total']


class DetalleCompraFilter(django_filters.FilterSet):
    compra           = django_filters.NumberFilter(field_name='compra_id')
    moto             = django_filters.NumberFilter(field_name='moto_id')
    cantidad_min     = django_filters.NumberFilter(field_name='cantidad', lookup_expr='gte')
    cantidad_max     = django_filters.NumberFilter(field_name='cantidad', lookup_expr='lte')
    precio_costo_min = django_filters.NumberFilter(field_name='precio_costo', lookup_expr='gte')
    precio_costo_max = django_filters.NumberFilter(field_name='precio_costo', lookup_expr='lte')

    class Meta:
        model  = DetalleCompra
        fields = ['compra', 'moto', 'cantidad', 'precio_costo']


class FinanciamientoFilter(django_filters.FilterSet):
    venta = django_filters.NumberFilter(field_name='venta_id')
    estado = django_filters.CharFilter(lookup_expr='icontains')
    monto_min = django_filters.NumberFilter(field_name='monto_financiado', lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name='monto_financiado', lookup_expr='lte')
    fecha_inicio = django_filters.DateFilter(field_name='fecha_inicio')

    class Meta:
        model = Financiamiento
        fields = ['venta', 'estado', 'monto_financiado', 'fecha_inicio']


class CuotaPagoFilter(django_filters.FilterSet):
    financiamiento = django_filters.NumberFilter(field_name='financiamiento_id')
    estado = django_filters.CharFilter(lookup_expr='icontains')
    fecha_vencimiento = django_filters.DateFilter(field_name='fecha_vencimiento')
    monto_min = django_filters.NumberFilter(field_name='monto', lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name='monto', lookup_expr='lte')

    class Meta:
        model = CuotaPago
        fields = ['financiamiento', 'estado', 'fecha_vencimiento', 'monto']


class HistorialPrecioFilter(django_filters.FilterSet):
    moto          = django_filters.NumberFilter(field_name='moto_id')
    usuario       = django_filters.NumberFilter(field_name='usuario_id')
    fecha_min     = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_max     = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
    precio_min    = django_filters.NumberFilter(field_name='precio_nuevo', lookup_expr='gte')
    precio_max    = django_filters.NumberFilter(field_name='precio_nuevo', lookup_expr='lte')

    class Meta:
        model  = HistorialPrecio
        fields = ['moto', 'usuario', 'fecha_min', 'fecha_max']


class ResenaFilter(django_filters.FilterSet):
    moto     = django_filters.NumberFilter(field_name='moto_id')
    cliente  = django_filters.NumberFilter(field_name='cliente_id')
    rating   = django_filters.NumberFilter(field_name='rating')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    fecha_min  = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_max  = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')

    class Meta:
        model  = Resena
        fields = ['moto', 'cliente', 'rating']


class LogsActividadFilter(django_filters.FilterSet):
    usuario     = django_filters.NumberFilter(field_name='usuario_id')
    accion      = django_filters.CharFilter(lookup_expr='icontains')
    entidad     = django_filters.CharFilter(lookup_expr='icontains')
    fecha_desde = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='gte')
    fecha_hasta = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='lte')

    class Meta:
        model  = LogsActividad
        fields = ['usuario', 'accion', 'entidad']