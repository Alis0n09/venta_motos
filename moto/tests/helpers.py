import itertools
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from moto.models import (
    Usuario, Cliente, Staff, Moto, Venta, DetalleVenta,
    Posventa, Garantia, Mantenimiento, Marca, Categoria,
)


_cedula_counter = itertools.count(1)
_marca_counter = itertools.count(1)


def _generar_cedula():
    return str(next(_cedula_counter)).zfill(10)


def create_user(username='user', email=None, password='Pass1234!', **kwargs):
    email = email or f'{username}@test.com'
    kwargs.setdefault('cedula', _generar_cedula())
    return Usuario.objects.create_user(
        username=username,
        email=email,
        password=password,
        **kwargs
    )


def create_staff_user(username='staffuser', email=None, password='Admin1234!'):
    email = email or f'{username}@test.com'
    return Usuario.objects.create_user(
        username=username,
        email=email,
        password=password,
        cedula=_generar_cedula(),
        is_staff=True
    )


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def auth_client(user):
    client = APIClient()
    access, _ = get_tokens(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
    return client


def create_cliente(
    nombre="Juan",
    apellido="Perez",
    cedula="0102030405",
    telefono="0999999999",
    correo=None,
    email=None,
    direccion="Quito",
    usuario=None,
):
    return Cliente.objects.create(
        usuario=usuario,
        nombre=nombre,
        apellido=apellido,
        cedula=cedula,
        telefono=telefono,
        correo=correo or email or "juan.perez@gmail.com",
        direccion=direccion,
    )


def create_vendedor(
    username='vendedor1',
    nombre="Carlos",
    apellido="Lopez",
    cedula=None,
    telefono="0988888888",
    correo=None,
    email=None,
    rol=Staff.Rol.VENDEDOR,
    password='Pass1234!',
):
    correo = correo or email or "carlos.lopez@gmail.com"
    cedula = cedula or _generar_cedula()

    usuario = Usuario.objects.create_user(
        username=username,
        email=correo,
        password=password,
        first_name=nombre,
        last_name=apellido,
        cedula=cedula,
        telefono=telefono,
        is_staff=True,
    )

    return Staff.objects.create(usuario=usuario, rol=rol)


def create_marca(nombre=None, pais_origen="Japón", activa=True):
    if nombre is None:
        nombre = f"Marca-{next(_marca_counter)}"
    return Marca.objects.create(nombre=nombre, pais_origen=pais_origen, activa=activa)


def create_categoria(nombre=None, descripcion="Categoría de prueba"):
    if nombre is None:
        nombre = f"Categoria-{next(_marca_counter)}"
    return Categoria.objects.create(nombre=nombre, descripcion=descripcion)


def create_moto(
    marca=None,
    categoria=None,
    modelo="CBR 500R",
    anio=2023,
    color="Rojo",
    precio=8500.00,
    cilindraje=500,
    estado="disponible",
    descripcion=None,
):
    if marca is None:
        marca = create_marca()
    elif isinstance(marca, str):
        marca, _ = Marca.objects.get_or_create(nombre=marca, defaults={'pais_origen': 'Japón'})

    if isinstance(categoria, str):
        categoria, _ = Categoria.objects.get_or_create(nombre=categoria)

    return Moto.objects.create(
        marca=marca,
        categoria=categoria,
        modelo=modelo,
        anio=anio,
        color=color,
        precio=precio,
        cilindraje=cilindraje,
        estado=estado,
    )


def create_venta(
    cliente=None,
    vendedor=None,
    total=3500,
    metodo_pago="efectivo",
):
    if cliente is None:
        cliente = create_cliente()

    if vendedor is None:
        vendedor = create_vendedor()

    return Venta.objects.create(
        cliente=cliente,
        vendedor=vendedor,
        total=total,
        metodo_pago=metodo_pago,
    )


def add_detalle_venta(venta=None, moto=None, cantidad=1, precio_unitario=None):
    if venta is None:
        venta = create_venta()

    if moto is None:
        moto = create_moto()

    if precio_unitario is None:
        precio_unitario = moto.precio

    return DetalleVenta.objects.create(
        venta=venta,
        moto=moto,
        cantidad=cantidad,
        precio_unitario=precio_unitario
    )


def create_posventa(venta=None, estado='pendiente', observaciones=''):
    if venta is None:
        cliente = create_cliente(cedula=_generar_cedula())
        username = f'vendedor_{_generar_cedula()}'
        vendedor = create_vendedor(username=username, cedula=_generar_cedula())
        venta = create_venta(cliente=cliente, vendedor=vendedor)
    return Posventa.objects.create(
        venta=venta,
        estado=estado,
        observaciones=observaciones
    )


def create_garantia(
    posventa=None,
    fecha_inicio=None,
    fecha_fin=None,
    tipo_cobertura='Cobertura completa',
    estado='activa'
):
    from datetime import date
    if posventa is None:
        posventa = create_posventa()
    if fecha_inicio is None:
        fecha_inicio = date.today()
    if fecha_fin is None:
        fecha_fin = date(date.today().year + 1, date.today().month, date.today().day)
    return Garantia.objects.create(
        posventa=posventa,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_cobertura=tipo_cobertura,
        estado=estado
    )


def create_mantenimiento(
    posventa=None,
    moto=None,
    tipo_mantenimiento='preventivo',
    fecha_programada=None,
    costo=150.00,
    estado='pendiente',
    descripcion='Mantenimiento de rutina'
):
    from datetime import date
    if posventa is None:
        posventa = create_posventa()
    if moto is None:
        moto = create_moto()
    if fecha_programada is None:
        fecha_programada = date.today()
    return Mantenimiento.objects.create(
        posventa=posventa,
        moto=moto,
        tipo_mantenimiento=tipo_mantenimiento,
        fecha_programada=fecha_programada,
        costo=costo,
        estado=estado,
        descripcion=descripcion
    )