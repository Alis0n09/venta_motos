# moto/tests/test_marcas.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client
from moto.models import Marca


class MarcaPermissionTests(TestCase):

    def setUp(self):
        self.user  = create_user('eve')
        self.staff = create_staff_user()
        self.marca = Marca.objects.create(nombre='Honda', pais_origen='Japón')

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/marcas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/marcas/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/marcas/', {
            'nombre': 'Yamaha',
            'pais_origen': 'Japón',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/marcas/', {
            'nombre': 'Suzuki',
            'pais_origen': 'Japón',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/marcas/{self.marca.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class MarcaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        Marca.objects.create(nombre='Yamaha', pais_origen='Japón', activa=True)
        Marca.objects.create(nombre='KTM', pais_origen='Austria', activa=False)

    def test_search_by_nombre(self):
        resp = self.client.get('/api/marcas/?search=yamaha')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_pais_origen(self):
        resp = self.client.get('/api/marcas/?pais_origen=Austria')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'KTM')

    def test_filter_by_activa(self):
        resp = self.client.get('/api/marcas/?activa=false')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'KTM')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/marcas/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'activas', 'detail']:
            self.assertIn(field, resp.data)