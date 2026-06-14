# moto/tests/test_proveedores.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client
from moto.models import Proveedor


def create_proveedor(
    empresa='Yamaha Ecuador',
    contacto='Pedro Gómez',
    correo='pedro@yamaha.com.ec',
    pais='Ecuador',
):
    return Proveedor.objects.create(
        empresa=empresa,
        contacto=contacto,
        correo=correo,
        pais=pais,
    )


class ProveedorPermissionTests(TestCase):

    def setUp(self):
        self.user      = create_user('prov_user')
        self.staff     = create_staff_user('prov_staff')
        self.proveedor = create_proveedor()

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/proveedores/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/proveedores/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/proveedores/', {
            'empresa': 'Honda Colombia',
            'contacto': 'Ana Ruiz',
            'correo': 'ana@honda.com.co',
            'pais': 'Colombia',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/proveedores/', {
            'empresa': 'Honda Colombia',
            'contacto': 'Ana Ruiz',
            'correo': 'ana@honda.com.co',
            'pais': 'Colombia',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/proveedores/{self.proveedor.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class ProveedorFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('prov_filter'))

        create_proveedor(
            empresa='Yamaha Ecuador',
            contacto='Pedro Gómez',
            correo='pedro@yamaha.com.ec',
            pais='Ecuador',
        )
        create_proveedor(
            empresa='Suzuki Perú',
            contacto='Laura Díaz',
            correo='laura@suzuki.com.pe',
            pais='Perú',
        )

    def test_search_by_empresa(self):
        resp = self.client.get('/api/proveedores/?search=yamaha')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_pais(self):
        resp = self.client.get('/api/proveedores/?pais=Ecuador')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['empresa'], 'Yamaha Ecuador')

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/proveedores/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
