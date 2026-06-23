from django.test import TestCase
from rest_framework import status

from moto.models import NotificacionesCliente
from moto.tests.helpers import create_user, create_staff_user, auth_client, create_cliente, create_notificacion_cliente


class NotificacionesClientePermissionTests(TestCase):
    def setUp(self):
        self.user   = create_user('notif_user')
        self.staff  = create_staff_user('notif_staff')
        self.cliente = create_cliente()
        self.obj = NotificacionesCliente.objects.create(
            cliente=self.cliente,
            tipo='info',
            mensaje='Bienvenido',
        )

    def _payload(self):
        return {
            'cliente': self.cliente.id,
            'tipo': 'promocion',
            'mensaje': 'Descuento especial',
        }

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/notificaciones-cliente/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/notificaciones-cliente/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/notificaciones-cliente/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/notificaciones-cliente/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/notificaciones-cliente/{self.obj.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class NotificacionesClienteFilterTests(TestCase):
    def setUp(self):
        self.user   = create_user('notif_filter')
        self.client_api = auth_client(self.user)
        self.cliente1 = create_cliente(cedula='1111111111', nombre='Ana')
        self.cliente2 = create_cliente(cedula='2222222222', nombre='Luis')
        self.n1 = create_notificacion_cliente(
            cliente=self.cliente1, tipo='info', mensaje='Bienvenido Ana', leido=False,
        )
        self.n2 = create_notificacion_cliente(
            cliente=self.cliente2, tipo='promocion', mensaje='Oferta especial', leido=True,
        )

    def test_filter_by_cliente(self):
        resp = self.client_api.get(f'/api/notificaciones-cliente/?cliente={self.cliente1.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_leido(self):
        resp = self.client_api.get('/api/notificaciones-cliente/?leido=True')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_tipo(self):
        resp = self.client_api.get('/api/notificaciones-cliente/?tipo=info')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_mensaje(self):
        resp = self.client_api.get('/api/notificaciones-cliente/?search=Oferta')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client_api.get('/api/notificaciones-cliente/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'no_leidas', 'detail']:
            self.assertIn(field, resp.data)
