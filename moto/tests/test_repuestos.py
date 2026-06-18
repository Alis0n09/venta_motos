# moto/tests/test_repuestos.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client
from moto.models import Repuesto, Marca


class RepuestoPermissionTests(TestCase):

    def setUp(self):
        self.user  = create_user('eve')
        self.staff = create_staff_user()
        self.marca = Marca.objects.create(nombre='Honda', pais_origen='Japón')
        self.repuesto = Repuesto.objects.create(
            nombre='Filtro de aceite',
            marca_compatible=self.marca,
            stock=10,
            precio=15.50
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/repuestos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/repuestos/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/repuestos/', {
            'nombre': 'Pastillas de freno',
            'marca_compatible': self.marca.id,
            'stock': 5,
            'precio': 25.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/repuestos/', {
            'nombre': 'Cadena',
            'marca_compatible': self.marca.id,
            'stock': 8,
            'precio': 45.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/repuestos/{self.repuesto.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_with_negative_precio_fails(self):
        resp = auth_client(self.staff).post('/api/repuestos/', {
            'nombre': 'Espejo',
            'marca_compatible': self.marca.id,
            'stock': 3,
            'precio': -10.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RepuestoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        self.honda = Marca.objects.create(nombre='Honda', pais_origen='Japón')
        self.yamaha = Marca.objects.create(nombre='Yamaha', pais_origen='Japón')

        Repuesto.objects.create(nombre='Bujía', marca_compatible=self.honda, stock=20, precio=5.00)
        Repuesto.objects.create(nombre='Cable de embrague', marca_compatible=self.yamaha, stock=2, precio=12.00)

    def test_search_by_nombre(self):
        resp = self.client.get('/api/repuestos/?search=Buj')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_marca_compatible(self):
        resp = self.client.get(f'/api/repuestos/?marca_compatible={self.yamaha.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'Cable de embrague')

    def test_filter_by_stock_max(self):
        resp = self.client.get('/api/repuestos/?stock_max=5')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['nombre'], 'Cable de embrague')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/repuestos/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)