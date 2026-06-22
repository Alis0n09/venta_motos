# moto/tests/test_historial_precio.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_moto
from moto.models import HistorialPrecio


class HistorialPrecioPermissionTests(TestCase):

    def setUp(self):
        self.user  = create_user('eve')
        self.staff = create_staff_user()
        self.moto  = create_moto()
        self.historial = HistorialPrecio.objects.create(
            moto=self.moto,
            precio_anterior=8000.00,
            precio_nuevo=8500.00,
            usuario=self.staff,
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/historial-precios/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/historial-precios/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/historial-precios/', {
            'moto': self.moto.id,
            'precio_anterior': 8500.00,
            'precio_nuevo': 9000.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/historial-precios/', {
            'moto': self.moto.id,
            'precio_anterior': 8500.00,
            'precio_nuevo': 9000.00,
            'usuario': self.staff.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/historial-precios/{self.historial.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_precio_igual_falla(self):
        resp = auth_client(self.staff).post('/api/historial-precios/', {
            'moto': self.moto.id,
            'precio_anterior': 8500.00,
            'precio_nuevo': 8500.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_precio_negativo_falla(self):
        resp = auth_client(self.staff).post('/api/historial-precios/', {
            'moto': self.moto.id,
            'precio_anterior': 8500.00,
            'precio_nuevo': -100.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class HistorialPrecioFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        self.staff  = create_staff_user()

        self.moto1 = create_moto()
        self.moto2 = create_moto()

        HistorialPrecio.objects.create(
            moto=self.moto1,
            precio_anterior=5000.00,
            precio_nuevo=5500.00,
            usuario=self.staff,
        )
        HistorialPrecio.objects.create(
            moto=self.moto2,
            precio_anterior=8000.00,
            precio_nuevo=9000.00,
            usuario=self.staff,
        )

    def test_filter_by_moto(self):
        resp = self.client.get(f'/api/historial-precios/?moto={self.moto1.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_precio_min(self):
        resp = self.client.get('/api/historial-precios/?precio_min=8000')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/historial-precios/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)