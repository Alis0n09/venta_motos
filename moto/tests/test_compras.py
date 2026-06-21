from django.test import TestCase
from rest_framework import status

from moto.models import Compra, Proveedor, Sucursal
from moto.tests.helpers import create_user, create_staff_user, auth_client


def _make_proveedor(empresa='Yamaha Ecuador'):
    return Proveedor.objects.create(empresa=empresa, pais='Ecuador')


def _make_sucursal(nombre='Sucursal Norte'):
    return Sucursal.objects.create(
        nombre=nombre, direccion='Av. América', ciudad='Quito'
    )


class CompraPermissionTests(TestCase):
    def setUp(self):
        self.user      = create_user('com_user')
        self.staff     = create_staff_user('com_staff')
        self.proveedor = _make_proveedor()
        self.sucursal  = _make_sucursal()
        self.obj = Compra.objects.create(
            proveedor=self.proveedor,
            sucursal_destino=self.sucursal,
            total=5000,
        )

    def _payload(self):
        return {
            'proveedor': self.proveedor.id,
            'sucursal_destino': self.sucursal.id,
            'total': '3000.00',
        }

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/compras/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/compras/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/compras/', self._payload())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/compras/', self._payload())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/compras/{self.obj.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class CompraFilterTests(TestCase):
    def setUp(self):
        self.client    = auth_client(create_user('com_filter'))
        self.proveedor = _make_proveedor('Yamaha Ecuador')
        self.sucursal  = _make_sucursal()
        Compra.objects.create(
            proveedor=self.proveedor, sucursal_destino=self.sucursal, total=5000
        )
        otro = _make_proveedor('Honda Ecuador')
        Compra.objects.create(
            proveedor=otro, sucursal_destino=self.sucursal, total=2000
        )

    def test_search_by_proveedor(self):
        resp = self.client.get('/api/compras/?search=yamaha')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_proveedor(self):
        resp = self.client.get(f'/api/compras/?proveedor={self.proveedor.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_total_min(self):
        resp = self.client.get('/api/compras/?total_min=4000')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/compras/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_registros', 'suma_total']:
            self.assertIn(field, resp.data)
