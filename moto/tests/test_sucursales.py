# moto/tests/test_sucursales.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client
from moto.models import Sucursal


def create_sucursal(
    nombre='Sucursal Norte',
    direccion='Av. América N32-145',
    ciudad='Quito',
    telefono='022345678',
):
    return Sucursal.objects.create(
        nombre=nombre,
        direccion=direccion,
        ciudad=ciudad,
        telefono=telefono,
    )


class SucursalPermissionTests(TestCase):

    def setUp(self):
        self.user     = create_user('suc_user')
        self.staff    = create_staff_user('suc_staff')
        self.sucursal = create_sucursal()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/sucursales/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/sucursales/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/sucursales/', {
            'nombre': 'Sucursal Sur',
            'direccion': 'Av. Maldonado S12-34',
            'ciudad': 'Quito',
            'telefono': '022345679',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/sucursales/', {
            'nombre': 'Sucursal Sur',
            'direccion': 'Av. Maldonado S12-34',
            'ciudad': 'Quito',
            'telefono': '022345679',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/sucursales/{self.sucursal.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class SucursalFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('suc_filter'))

        create_sucursal(
            nombre='Sucursal Norte',
            direccion='Av. América N32-145',
            ciudad='Quito',
            telefono='022345678',
        )
        create_sucursal(
            nombre='Sucursal Centro',
            direccion='Calle Bolívar 10-45',
            ciudad='Guayaquil',
            telefono='042345678',
        )

    def test_search_by_nombre(self):
        resp = self.client.get('/api/sucursales/?search=norte')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_ciudad(self):
        resp = self.client.get('/api/sucursales/?ciudad=Quito')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'Sucursal Norte')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/sucursales/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
