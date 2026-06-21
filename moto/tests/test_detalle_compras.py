from django.test import TestCase
from rest_framework import status

from moto.models import Compra, DetalleCompra, Proveedor, Sucursal
from moto.tests.helpers import create_user, create_staff_user, auth_client, create_moto


def _make_compra():
    proveedor = Proveedor.objects.create(empresa='Proveedor DC', pais='Ecuador')
    sucursal  = Sucursal.objects.create(
        nombre='Sucursal DC', direccion='Calle 1', ciudad='Guayaquil'
    )
    return Compra.objects.create(
        proveedor=proveedor, sucursal_destino=sucursal, total=9000
    )


class DetalleCompraPermissionTests(TestCase):
    def setUp(self):
        self.user   = create_user('dc_user')
        self.staff  = create_staff_user('dc_staff')
        self.compra = _make_compra()
        self.moto   = create_moto()
        self.obj = DetalleCompra.objects.create(
            compra=self.compra, moto=self.moto, cantidad=2, precio_costo=4500
        )

    def _payload(self):
        return {
            'compra': self.compra.id,
            'moto': self.moto.id,
            'cantidad': 1,
            'precio_costo': '3000.00',
        }

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/detalle-compras/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/detalle-compras/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/detalle-compras/', self._payload())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/detalle-compras/', self._payload())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/detalle-compras/{self.obj.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DetalleCompraFilterTests(TestCase):
    def setUp(self):
        self.client = auth_client(create_user('dc_filter'))
        self.compra = _make_compra()
        self.moto   = create_moto()
        DetalleCompra.objects.create(
            compra=self.compra, moto=self.moto, cantidad=2, precio_costo=4500
        )

    def test_filter_by_compra(self):
        resp = self.client.get(f'/api/detalle-compras/?compra={self.compra.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_cantidad_min(self):
        resp = self.client.get('/api/detalle-compras/?cantidad_min=1')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/detalle-compras/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
