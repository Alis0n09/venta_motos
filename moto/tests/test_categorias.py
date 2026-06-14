# moto/tests/test_categorias.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client
from moto.models import Categoria


class CategoriaPermissionTests(TestCase):

    def setUp(self):
        self.user      = create_user('eve')
        self.staff     = create_staff_user()
        self.categoria = Categoria.objects.create(nombre='Deportiva', descripcion='Motos de alto rendimiento')

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/categorias/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/categorias/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/categorias/', {
            'nombre': 'Urbana',
            'descripcion': 'Para ciudad',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/categorias/', {
            'nombre': 'Touring',
            'descripcion': 'Para viajes largos',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/categorias/{self.categoria.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class CategoriaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        Categoria.objects.create(nombre='Off-road', descripcion='Para terrenos difíciles')
        Categoria.objects.create(nombre='Scooter', descripcion='Uso urbano ligero')

    def test_search_by_nombre(self):
        resp = self.client.get('/api/categorias/?search=scooter')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/categorias/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)