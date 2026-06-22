# moto/admin.py

from django.contrib import admin
from moto.models import (
    Cliente, Usuario, Staff, Moto, Venta, DetalleVenta,
    Sucursal, Direccion, Proveedor,
    Posventa, Garantia, Mantenimiento,
    Categoria, Marca, Repuesto,
    Inventario, SucursalStaff,
    Compra, DetalleCompra,
    HistorialPrecio, Resena,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'apellido', 'cedula', 'telefono']
    search_fields = ['nombre', 'apellido', 'cedula', 'telefono']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ['id', 'username', 'first_name', 'last_name', 'telefono', 'cedula']
    search_fields = ['username', 'first_name', 'last_name', 'email']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display  = ['id', 'usuario', 'rol']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name']
    list_filter   = ['rol']


@admin.register(Moto)
class MotoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'marca', 'categoria', 'modelo', 'anio', 'color', 'precio', 'stock']
    search_fields = ['marca__nombre', 'modelo', 'color']
    list_filter   = ['marca', 'categoria', 'anio', 'color']
    list_editable = ['precio', 'stock']


class DetalleVentaInline(admin.TabularInline):
    model  = DetalleVenta
    extra  = 0
    fields = ['moto', 'cantidad', 'precio_unitario']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cliente', 'vendedor', 'total']
    search_fields = [
        'cliente__nombre',
        'cliente__apellido',
        'cliente__cedula',
        'vendedor__usuario__username',
        'vendedor__usuario__first_name',
        'vendedor__usuario__last_name',
    ]
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'venta', 'moto', 'cantidad', 'precio_unitario']
    list_filter   = ['moto']
    search_fields = ['moto__marca__nombre', 'moto__modelo', 'venta__id']


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'ciudad', 'direccion', 'telefono']
    search_fields = ['nombre', 'ciudad']
    list_filter   = ['ciudad']


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cliente', 'calle', 'ciudad', 'provincia', 'principal']
    search_fields = ['calle', 'ciudad', 'provincia']
    list_filter   = ['ciudad', 'provincia', 'principal']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display  = ['id', 'empresa', 'contacto', 'correo', 'pais']
    search_fields = ['empresa', 'contacto', 'pais']
    list_filter   = ['pais']


@admin.register(Posventa)
class PosventaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'venta', 'fecha_apertura', 'fecha_cierre', 'estado']
    search_fields = ['estado', 'observaciones']
    list_filter   = ['estado']


@admin.register(Garantia)
class GarantiaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'posventa', 'fecha_inicio', 'fecha_fin', 'tipo_cobertura', 'estado']
    search_fields = ['tipo_cobertura', 'estado']
    list_filter   = ['estado', 'tipo_cobertura']


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'posventa', 'moto', 'tipo_mantenimiento', 'fecha_programada', 'costo', 'estado']
    search_fields = ['descripcion', 'tipo_mantenimiento', 'estado']
    list_filter   = ['estado', 'tipo_mantenimiento']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'pais_origen', 'activa']
    search_fields = ['nombre', 'pais_origen']
    list_filter   = ['activa']


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'marca_compatible', 'stock', 'precio']
    search_fields = ['nombre', 'marca_compatible__nombre']
    list_filter   = ['marca_compatible']


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display  = ['id', 'moto', 'sucursal', 'cantidad', 'ubicacion_bodega']
    search_fields = ['moto__modelo', 'moto__marca__nombre', 'sucursal__nombre']
    list_filter   = ['sucursal']
    list_editable = ['cantidad']


@admin.register(SucursalStaff)
class SucursalStaffAdmin(admin.ModelAdmin):
    list_display  = ['id', 'staff', 'sucursal', 'fecha_asignacion']
    search_fields = ['staff__usuario__first_name', 'staff__usuario__last_name', 'sucursal__nombre']
    list_filter   = ['sucursal']


class DetalleCompraInline(admin.TabularInline):
    model  = DetalleCompra
    extra  = 0
    fields = ['moto', 'cantidad', 'precio_costo']


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display  = ['id', 'proveedor', 'sucursal_destino', 'fecha', 'total']
    search_fields = ['proveedor__empresa', 'sucursal_destino__nombre']
    list_filter   = ['sucursal_destino', 'fecha']
    inlines       = [DetalleCompraInline]


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display  = ['id', 'compra', 'moto', 'cantidad', 'precio_costo']
    search_fields = ['moto__marca__nombre', 'moto__modelo']
    list_filter   = ['moto']


@admin.register(HistorialPrecio)
class HistorialPrecioAdmin(admin.ModelAdmin):
    list_display  = ['id', 'moto', 'precio_anterior', 'precio_nuevo', 'fecha', 'usuario']
    search_fields = ['moto__modelo', 'moto__marca__nombre', 'usuario__first_name', 'usuario__last_name']
    list_filter   = ['moto', 'fecha']
    readonly_fields = ['fecha']


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'moto', 'cliente', 'rating', 'fecha']
    search_fields = ['moto__modelo', 'moto__marca__nombre', 'cliente__nombre', 'cliente__apellido', 'comentario']
    list_filter   = ['rating', 'moto']
    readonly_fields = ['fecha']