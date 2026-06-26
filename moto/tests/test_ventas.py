# moto/tests/test_ventas.py

from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user,
    create_staff_user,
    create_staff_with_rol,
    auth_client,
    create_cliente,
    create_vendedor,
    create_venta,
)


class VentaPermissionTests(TestCase):

    def setUp(self):
        self.user      = create_user('eve')
        self.staff     = create_staff_with_rol('ventas_admin', 'admin')
        self.cliente   = create_cliente()
        self.vendedor  = create_vendedor()
        self.venta     = create_venta(
            cliente=self.cliente,
            vendedor=self.vendedor,
            total=3500
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/ventas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/ventas/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/ventas/', {
            'cliente': self.cliente.id,
            'vendedor': self.vendedor.id,
            'total': 4500
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        cliente = create_cliente(
            nombre='Ana',
            apellido='Torres',
            cedula='8888888888',
            telefono='0988888888',
            email='ana@test.com',
            direccion='Dirección cliente'
        )

        vendedor = create_vendedor(
            username='luismora',
            nombre='Luis',
            apellido='Mora',
            cedula='7777777777',
            telefono='0977777777',
            email='luis@test.com',
        )

        resp = auth_client(self.staff).post('/api/ventas/', {
            'cliente': cliente.id,
            'vendedor': vendedor.id,
            'total': 4500
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/ventas/{self.venta.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class VentaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        cliente_1 = create_cliente(
            nombre='Carlos',
            apellido='Gómez',
            cedula='0102030405',
            telefono='0999999999',
            email='carlos@test.com',
            direccion='Dirección Carlos'
        )

        vendedor_1 = create_vendedor(
            username='pedromena',
            nombre='Pedro',
            apellido='Mena',
            cedula='1102030405',
            telefono='0988888888',
            email='pedro@test.com',
        )

        cliente_2 = create_cliente(
            nombre='María',
            apellido='Torres',
            cedula='0203040506',
            telefono='0977777777',
            email='maria@test.com',
            direccion='Dirección María'
        )

        vendedor_2 = create_vendedor(
            username='sofialopez',
            nombre='Sofía',
            apellido='López',
            cedula='1203040506',
            telefono='0966666666',
            email='sofia@test.com',
        )

        create_venta(
            cliente=cliente_1,
            vendedor=vendedor_1,
            total=3500
        )

        create_venta(
            cliente=cliente_2,
            vendedor=vendedor_2,
            total=4500
        )

    def test_filter_by_cliente(self):
        cliente = create_cliente(
            nombre='Juan',
            apellido='Pérez',
            cedula='0304050607',
            telefono='0955555555',
            email='juan@test.com',
            direccion='Dirección Juan'
        )

        vendedor = create_vendedor(
            username='andrescastro',
            nombre='Andrés',
            apellido='Castro',
            cedula='1304050607',
            telefono='0944444444',
            email='andres@test.com',
        )

        create_venta(
            cliente=cliente,
            vendedor=vendedor,
            total=5000
        )

        resp = self.client.get(f'/api/ventas/?cliente={cliente.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['cliente'], cliente.id)

    def test_filter_by_vendedor(self):
        cliente = create_cliente(
            nombre='Paula',
            apellido='Reyes',
            cedula='0405060708',
            telefono='0933333333',
            email='paula@test.com',
            direccion='Dirección Paula'
        )

        vendedor = create_vendedor(
            username='mateoruiz',
            nombre='Mateo',
            apellido='Ruiz',
            cedula='1405060708',
            telefono='0922222222',
            email='mateo@test.com',
        )

        create_venta(
            cliente=cliente,
            vendedor=vendedor,
            total=6000
        )

        resp = self.client.get(f'/api/ventas/?vendedor={vendedor.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['vendedor'], vendedor.id)

    def test_filter_by_total(self):
        resp = self.client.get('/api/ventas/?total=3500')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['total'], '3500.00')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/ventas/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)