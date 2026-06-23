from django.test import TestCase
from rest_framework import status

from moto.models import HistorialCliente
from moto.tests.helpers import create_user, create_staff_user, auth_client, create_cliente


class HistorialClientePermissionTests(TestCase):
    def setUp(self):
        self.user   = create_user('hist_user')
        self.staff  = create_staff_user('hist_staff')
        self.cliente = create_cliente()
        self.obj = HistorialCliente.objects.create(
            cliente=self.cliente,
            tipo_evento='compra',
            detalle={'monto': 500},
        )

    def _payload(self):
        return {
            'cliente': self.cliente.id,
            'tipo_evento': 'actualizacion',
            'detalle': {'campo': 'telefono'},
        }

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/historial-cliente/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/historial-cliente/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/historial-cliente/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/historial-cliente/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/historial-cliente/{self.obj.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class HistorialClienteFilterTests(TestCase):
    def setUp(self):
        self.user   = create_user('hist_filter')
        self.client_api = auth_client(self.user)
        self.cliente1 = create_cliente(cedula='1111111111', nombre='Ana')
        self.cliente2 = create_cliente(cedula='2222222222', nombre='Luis')
        self.h1 = HistorialCliente.objects.create(
            cliente=self.cliente1, tipo_evento='compra', detalle={'monto': 500},
        )
        self.h2 = HistorialCliente.objects.create(
            cliente=self.cliente2, tipo_evento='actualizacion', detalle={'campo': 'email'},
        )

    def test_filter_by_cliente(self):
        resp = self.client_api.get(f'/api/historial-cliente/?cliente={self.cliente1.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_tipo_evento(self):
        resp = self.client_api.get('/api/historial-cliente/?search=compra')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client_api.get('/api/historial-cliente/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
