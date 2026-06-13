# moto/tests/test_motos.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_moto


class MotoPermissionTests(TestCase):

    def setUp(self):
        self.user  = create_user('eve')
        self.staff = create_staff_user()
        self.moto  = create_moto()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/motos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/motos/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/motos/', {
            'marca': 'Honda',
            'modelo': 'CBR',
            'anio': 2024,
            'color': 'Rojo',
            'precio': 4500,
            'stock': 5,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/motos/', {
            'marca': 'Yamaha',
            'modelo': 'FZ',
            'anio': 2024,
            'color': 'Negro',
            'precio': 3500,
            'stock': 10,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/motos/{self.moto.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class MotoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        create_moto(
            marca='Yamaha',
            modelo='FZ',
            anio=2024,
            color='Negro',
            precio=3500,
            stock=10,
        )

        create_moto(
            marca='Honda',
            modelo='CBR',
            anio=2023,
            color='Rojo',
            precio=4500,
            stock=5,
        )

    def test_search_by_marca(self):
        resp = self.client.get('/api/motos/?search=yamaha')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_modelo(self):
        resp = self.client.get('/api/motos/?search=cbr')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_marca(self):
        resp = self.client.get('/api/motos/?marca=Yamaha')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['marca'], 'Yamaha')

    def test_filter_by_anio(self):
        resp = self.client.get('/api/motos/?anio=2024')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['modelo'], 'FZ')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/motos/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)