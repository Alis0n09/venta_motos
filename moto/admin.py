# moto/admin.py

from django.contrib import admin
from moto.models import Cliente, Usuario, Staff, Moto, Venta, DetalleVenta, Sucursal, Direccion, Proveedor


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
    list_display  = ['id', 'marca', 'modelo', 'anio', 'color', 'precio', 'stock']
    search_fields = ['marca', 'modelo', 'color']
    list_filter   = ['marca', 'anio', 'color']
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
    search_fields = ['moto__marca', 'moto__modelo', 'venta__id']


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