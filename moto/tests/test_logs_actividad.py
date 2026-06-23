from django.test import TestCase
from rest_framework import status

from moto.models import LogsActividad
from moto.tests.helpers import create_user, create_staff_user, auth_client


class LogsActividadPermissionTests(TestCase):
    def setUp(self):
        self.usuario = create_user('log_user')
        self.staff   = create_staff_user('log_staff')
        self.obj = LogsActividad.objects.create(
            usuario=self.usuario,
            accion='crear',
            entidad='Cliente',
            datos_antes=None,
            datos_despues={'nombre': 'Juan'},
        )

    def _payload(self):
        return {
            'usuario': self.usuario.id,
            'accion': 'editar',
            'entidad': 'Moto',
            'datos_antes': {'precio': 5000},
            'datos_despues': {'precio': 6000},
        }

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.usuario).get('/api/logs-actividad/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/logs-actividad/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.usuario).post('/api/logs-actividad/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/logs-actividad/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/logs-actividad/{self.obj.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class LogsActividadFilterTests(TestCase):
    def setUp(self):
        self.user   = create_user('log_filter')
        self.client = auth_client(self.user)
        self.log1 = LogsActividad.objects.create(
            usuario=self.user,
            accion='crear',
            entidad='Cliente',
            datos_antes=None,
            datos_despues={'nombre': 'Juan'},
        )
        self.log2 = LogsActividad.objects.create(
            usuario=self.user,
            accion='eliminar',
            entidad='Moto',
            datos_antes={'modelo': 'CBR'},
            datos_despues=None,
        )

    def test_search_by_accion(self):
        resp = self.client.get('/api/logs-actividad/?search=crear')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_entidad(self):
        resp = self.client.get('/api/logs-actividad/?entidad=Cliente')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_usuario(self):
        resp = self.client.get(f'/api/logs-actividad/?usuario={self.user.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['count'], 2)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/logs-actividad/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
