# moto/tests/test_detalle_ventas.py

from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user,
    create_staff_user,
    auth_client,
    create_cliente,
    create_vendedor,
    create_moto,
    create_venta,
    add_detalle_venta,
)


class DetalleVentaPermissionTests(TestCase):

    def setUp(self):
        self.user      = create_user('eve')
        self.staff     = create_staff_user()
        self.cliente   = create_cliente()
        self.vendedor  = create_vendedor()
        self.moto      = create_moto()
        self.venta     = create_venta(cliente=self.cliente, vendedor=self.vendedor, total=3500)
        self.detalle_venta = add_detalle_venta(venta=self.venta, moto=self.moto, cantidad=1, precio_unitario=3500)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/detalle-ventas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/detalle-ventas/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/detalle-ventas/', {
            'venta': self.venta.id,
            'moto': self.moto.id,
            'cantidad': 1,
            'precio_unitario': 3500
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        moto = create_moto(marca='Honda', modelo='CBR', anio=2024, color='Rojo', precio=4500)
        resp = auth_client(self.staff).post('/api/detalle-ventas/', {
            'venta': self.venta.id,
            'moto': moto.id,
            'cantidad': 1,
            'precio_unitario': 4500
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/detalle-ventas/{self.detalle_venta.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DetalleVentaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        cliente_1 = create_cliente(nombre='Carlos', apellido='Gómez', cedula='0102030405', telefono='0999999999', email='carlos@test.com', direccion='Dirección Carlos')
        vendedor_1 = create_vendedor(username='pedromena', nombre='Pedro', apellido='Mena', cedula='1102030405', telefono='0988888888', email='pedro@test.com')
        moto_1 = create_moto(marca='Yamaha', modelo='FZ', anio=2024, color='Negro', precio=3500)
        venta_1 = create_venta(cliente=cliente_1, vendedor=vendedor_1, total=3500)
        add_detalle_venta(venta=venta_1, moto=moto_1, cantidad=1, precio_unitario=3500)

        cliente_2 = create_cliente(nombre='María', apellido='Torres', cedula='0203040506', telefono='0977777777', email='maria@test.com', direccion='Dirección María')
        vendedor_2 = create_vendedor(username='sofialopez', nombre='Sofía', apellido='López', cedula='1203040506', telefono='0966666666', email='sofia@test.com')
        moto_2 = create_moto(marca='Honda', modelo='CBR', anio=2023, color='Rojo', precio=4500)
        venta_2 = create_venta(cliente=cliente_2, vendedor=vendedor_2, total=9000)
        add_detalle_venta(venta=venta_2, moto=moto_2, cantidad=2, precio_unitario=4500)

    def test_filter_by_venta(self):
        cliente = create_cliente(nombre='Juan', apellido='Pérez', cedula='0304050607', telefono='0955555555', email='juan@test.com', direccion='Dirección Juan')
        vendedor = create_vendedor(username='andrescastro', nombre='Andrés', apellido='Castro', cedula='1304050607', telefono='0944444444', email='andres@test.com')
        moto = create_moto(marca='Suzuki', modelo='Gixxer', anio=2024, color='Azul', precio=5000)
        venta = create_venta(cliente=cliente, vendedor=vendedor, total=5000)
        add_detalle_venta(venta=venta, moto=moto, cantidad=1, precio_unitario=5000)

        resp = self.client.get(f'/api/detalle-ventas/?venta={venta.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['venta'], venta.id)

    def test_filter_by_moto(self):
        cliente = create_cliente(nombre='Paula', apellido='Reyes', cedula='0405060708', telefono='0933333333', email='paula@test.com', direccion='Dirección Paula')
        vendedor = create_vendedor(username='mateoruiz', nombre='Mateo', apellido='Ruiz', cedula='1405060708', telefono='0922222222', email='mateo@test.com')
        moto = create_moto(marca='Kawasaki', modelo='Ninja', anio=2024, color='Verde', precio=6000)
        venta = create_venta(cliente=cliente, vendedor=vendedor, total=6000)
        add_detalle_venta(venta=venta, moto=moto, cantidad=1, precio_unitario=6000)

        resp = self.client.get(f'/api/detalle-ventas/?moto={moto.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['moto'], moto.id)

    def test_filter_by_cantidad(self):
        resp = self.client.get('/api/detalle-ventas/?cantidad=2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['cantidad'], 2)

    def test_filter_by_precio_unitario(self):
        resp = self.client.get('/api/detalle-ventas/?precio_unitario=3500')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['precio_unitario'], '3500.00')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/detalle-ventas/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)