# moto/tests/test_inventario.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_moto
from moto.models import Inventario, Sucursal


class InventarioPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.moto = create_moto()
        self.sucursal = Sucursal.objects.create(nombre='Matriz', direccion='Av. Principal', ciudad='Quito')
        self.inventario = Inventario.objects.create(
            moto=self.moto,
            sucursal=self.sucursal,
            cantidad=10,
            ubicacion_bodega='Pasillo A'
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/inventario/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/inventario/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        moto2 = create_moto()
        resp = auth_client(self.user).post('/api/inventario/', {
            'moto': moto2.id,
            'sucursal': self.sucursal.id,
            'cantidad': 5,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        moto2 = create_moto()
        resp = auth_client(self.staff).post('/api/inventario/', {
            'moto': moto2.id,
            'sucursal': self.sucursal.id,
            'cantidad': 8,
            'ubicacion_bodega': 'Pasillo B',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/inventario/{self.inventario.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_duplicate_moto_sucursal(self):
        resp = auth_client(self.staff).post('/api/inventario/', {
            'moto': self.moto.id,
            'sucursal': self.sucursal.id,
            'cantidad': 3,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class InventarioFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        self.sucursal1 = Sucursal.objects.create(nombre='Norte', direccion='Calle 1', ciudad='Quito')
        self.sucursal2 = Sucursal.objects.create(nombre='Sur', direccion='Calle 2', ciudad='Guayaquil')

        moto1 = create_moto()
        moto2 = create_moto()

        Inventario.objects.create(moto=moto1, sucursal=self.sucursal1, cantidad=15)
        Inventario.objects.create(moto=moto2, sucursal=self.sucursal2, cantidad=3)

    def test_filter_by_sucursal(self):
        resp = self.client.get(f'/api/inventario/?sucursal={self.sucursal2.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_cantidad_max(self):
        resp = self.client.get('/api/inventario/?cantidad_max=5')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/inventario/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)