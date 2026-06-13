# moto/tests/test_clientes.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_cliente


class ClientePermissionTests(TestCase):

    def setUp(self):
        self.user    = create_user('eve')
        self.staff   = create_staff_user()
        self.cliente = create_cliente()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/clientes/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/clientes/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/clientes/', {
            'nombre': 'Luis',
            'apellido': 'Mora',
            'cedula': '9999999999',
            'telefono': '0999999999',
            'correo': 'luis@test.com',
            'direccion': 'Dirección de prueba'
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/clientes/', {
            'nombre': 'Ana',
            'apellido': 'Torres',
            'cedula': '8888888888',
            'telefono': '0988888888',
            'correo': 'ana@test.com',
            'direccion': 'Dirección cliente'
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/clientes/{self.cliente.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class ClienteFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        create_cliente(
            nombre='Juan',
            apellido='Pérez',
            cedula='0102030405',
            telefono='0999999999',
            correo='juan@test.com',
            direccion='Dirección Juan'
        )

        create_cliente(
            nombre='María',
            apellido='Gómez',
            cedula='1102030405',
            telefono='0988888888',
            correo='maria@test.com',
            direccion='Dirección María'
        )

    def test_search_by_name(self):
        resp = self.client.get('/api/clientes/?search=juan')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_correo(self):
        resp = self.client.get('/api/clientes/?search=maria@test.com')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_cedula(self):
        resp = self.client.get('/api/clientes/?cedula=0102030405')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'Juan')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/clientes/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)