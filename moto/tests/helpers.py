# moto/tests/helpers.py

import itertools
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from moto.models import Usuario, Cliente, Staff, Moto, Venta, DetalleVenta


_cedula_counter = itertools.count(1)


def _generar_cedula():
    """Genera una cédula de prueba única tipo '0000000001', '0000000002', etc."""
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
    """Crea un Usuario con is_staff=True (para permisos a nivel Django/DRF)."""
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
    """Crea un Usuario + su perfil Staff asociado."""
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


def create_moto(
    marca="Honda",
    modelo="CBR 500R",
    anio=2023,
    color="Rojo",
    precio=8500.00,
    stock=5,
    cilindraje=500,
    estado="disponible",
    descripcion=None,
):
    return Moto.objects.create(
        marca=marca,
        modelo=modelo,
        anio=anio,
        color=color,
        precio=precio,
        stock=stock,
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