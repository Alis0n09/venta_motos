# moto/admin.py

from django.contrib import admin
from moto.models import Cliente, Usuario, Staff, Moto, Venta, DetalleVenta, Marca, Categoria, Repuesto


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


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'pais_origen', 'activa']
    search_fields = ['nombre', 'pais_origen']
    list_filter   = ['activa']
    list_editable = ['activa']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'marca_compatible', 'stock', 'precio']
    search_fields = ['nombre', 'marca_compatible__nombre']
    list_filter   = ['marca_compatible']
    list_editable = ['stock', 'precio']