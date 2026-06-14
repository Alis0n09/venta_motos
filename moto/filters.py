# moto/filters.py

import django_filters
from moto.models import Cliente, Staff, Moto, Venta, DetalleVenta, Sucursal, Direccion, Proveedor


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
    marca      = django_filters.CharFilter(lookup_expr='icontains')
    modelo     = django_filters.CharFilter(lookup_expr='icontains')
    color      = django_filters.CharFilter(lookup_expr='icontains')
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    stock_min  = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max  = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    anio_min   = django_filters.NumberFilter(field_name='anio', lookup_expr='gte')
    anio_max   = django_filters.NumberFilter(field_name='anio', lookup_expr='lte')

    class Meta:
        model  = Moto
        fields = ['marca', 'modelo', 'anio', 'color']


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
    moto_marca          = django_filters.CharFilter(field_name='moto__marca', lookup_expr='icontains')
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
