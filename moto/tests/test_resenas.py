# moto/tests/test_resenas.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_moto, create_cliente
from moto.models import Resena


class ResenaPermissionTests(TestCase):

    def setUp(self):
        self.user    = create_user('eve')
        self.staff   = create_staff_user()
        self.moto    = create_moto()
        self.cliente = create_cliente()
        self.resena  = Resena.objects.create(
            moto=self.moto,
            cliente=self.cliente,
            rating=4,
            comentario='Muy buena moto',
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/resenas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/resenas/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        cliente2 = create_cliente(cedula='9876543210', email='otro@test.com')
        resp = auth_client(self.user).post('/api/resenas/', {
            'moto': self.moto.id,
            'cliente': cliente2.id,
            'rating': 3,
            'comentario': 'Regular',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        cliente2 = create_cliente(cedula='9876543210', email='otro@test.com')
        resp = auth_client(self.staff).post('/api/resenas/', {
            'moto': self.moto.id,
            'cliente': cliente2.id,
            'rating': 5,
            'comentario': 'Excelente moto',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/resenas/{self.resena.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_rating_fuera_de_rango_falla(self):
        cliente2 = create_cliente(cedula='9876543210', email='otro@test.com')
        resp = auth_client(self.staff).post('/api/resenas/', {
            'moto': self.moto.id,
            'cliente': cliente2.id,
            'rating': 6,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resena_duplicada_falla(self):
        resp = auth_client(self.staff).post('/api/resenas/', {
            'moto': self.moto.id,
            'cliente': self.cliente.id,
            'rating': 2,
            'comentario': 'Duplicada',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ResenaFilterTests(TestCase):

    def setUp(self):
        self.client  = auth_client(create_user('filters'))

        self.moto1   = create_moto()
        self.moto2   = create_moto()
        self.cliente1 = create_cliente(cedula='1111111111', email='c1@test.com')
        self.cliente2 = create_cliente(cedula='2222222222', email='c2@test.com')

        Resena.objects.create(moto=self.moto1, cliente=self.cliente1, rating=5, comentario='Perfecta')
        Resena.objects.create(moto=self.moto2, cliente=self.cliente2, rating=2, comentario='Regular')

    def test_filter_by_moto(self):
        resp = self.client.get(f'/api/resenas/?moto={self.moto1.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_rating(self):
        resp = self.client.get('/api/resenas/?rating=5')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_rating_min(self):
        resp = self.client.get('/api/resenas/?rating_min=3')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/resenas/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'promedio_rating', 'detail']:
            self.assertIn(field, resp.data)