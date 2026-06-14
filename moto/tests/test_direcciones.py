# moto/tests/test_direcciones.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_cliente
from moto.models import Direccion


def create_direccion(cliente, calle='Calle Falsa 123', ciudad='Quito',
                     provincia='Pichincha', principal=True):
    return Direccion.objects.create(
        cliente=cliente,
        calle=calle,
        ciudad=ciudad,
        provincia=provincia,
        principal=principal,
    )


class DireccionPermissionTests(TestCase):

    def setUp(self):
        self.user      = create_user('dir_user')
        self.staff     = create_staff_user('dir_staff')
        self.cliente   = create_cliente(cedula='2200000001')
        self.direccion = create_direccion(self.cliente)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/direcciones/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/direcciones/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/direcciones/', {
            'cliente': self.cliente.id,
            'calle': 'Av. Siempre Viva 742',
            'ciudad': 'Quito',
            'provincia': 'Pichincha',
            'principal': False,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/direcciones/', {
            'cliente': self.cliente.id,
            'calle': 'Av. Siempre Viva 742',
            'ciudad': 'Quito',
            'provincia': 'Pichincha',
            'principal': False,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/direcciones/{self.direccion.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DireccionFilterTests(TestCase):

    def setUp(self):
        self.client  = auth_client(create_user('dir_filter'))
        self.cliente = create_cliente(cedula='2200000002')

        create_direccion(
            cliente=self.cliente,
            calle='Calle Falsa 123',
            ciudad='Quito',
            provincia='Pichincha',
            principal=True,
        )
        create_direccion(
            cliente=self.cliente,
            calle='Av. del Ejército 456',
            ciudad='Cuenca',
            provincia='Azuay',
            principal=False,
        )

    def test_search_by_calle(self):
        resp = self.client.get('/api/direcciones/?search=falsa')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_ciudad(self):
        resp = self.client.get('/api/direcciones/?ciudad=Quito')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['calle'], 'Calle Falsa 123')

    def test_filter_by_provincia(self):
        resp = self.client.get('/api/direcciones/?provincia=Azuay')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['ciudad'], 'Cuenca')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/direcciones/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
