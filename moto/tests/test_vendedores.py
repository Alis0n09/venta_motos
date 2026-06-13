# moto/tests/test_vendedores.py

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from moto.models import Staff
from .helpers import create_user, create_staff_user, auth_client, create_vendedor


class VendedorPermissionTests(TestCase):

    def setUp(self):
        self.user     = create_user('eve')
        self.staff    = create_staff_user()
        self.vendedor = create_vendedor()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/vendedores/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        resp = APIClient().get('/api/vendedores/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/vendedores/', {
            'rol': Staff.Rol.VENDEDOR,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        # El serializer de Vendedor es de solo lectura para los campos
        # de usuario (nombre, apellido, cedula, etc), así que solo
        # probamos que el staff pueda crear un Staff vinculado a un
        # usuario ya existente.
        nuevo_usuario = create_user('nuevoVendedor', email='nuevo@test.com')

        resp = auth_client(self.staff).post('/api/vendedores/', {
            'usuario': nuevo_usuario.id,
            'rol': Staff.Rol.VENDEDOR,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/vendedores/{self.vendedor.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class VendedorFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        create_vendedor(
            username='carlosg',
            nombre='Carlos',
            apellido='Gómez',
            cedula='0102030405',
            telefono='0999999999',
            correo='carlos@test.com',
        )

        create_vendedor(
            username='mariat',
            nombre='María',
            apellido='Torres',
            cedula='1102030405',
            telefono='0988888888',
            correo='maria@test.com',
        )

    def test_search_by_name(self):
        resp = self.client.get('/api/vendedores/?search=carlos')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_correo(self):
        resp = self.client.get('/api/vendedores/?search=maria@test.com')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_cedula(self):
        resp = self.client.get('/api/vendedores/?cedula=0102030405')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'Carlos')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/vendedores/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)