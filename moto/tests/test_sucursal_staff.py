# moto/tests/test_sucursal_staff.py

from django.test import TestCase
from rest_framework import status

from .helpers import create_user, create_staff_user, auth_client, create_vendedor
from moto.models import SucursalStaff, Sucursal


class SucursalStaffPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.vendedor = create_vendedor()
        self.sucursal = Sucursal.objects.create(nombre='Matriz', direccion='Av. Principal', ciudad='Quito')
        self.asignacion = SucursalStaff.objects.create(
            staff=self.vendedor,
            sucursal=self.sucursal,
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/sucursal-staff/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/sucursal-staff/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        vendedor2 = create_vendedor(username='vendedor2')
        resp = auth_client(self.user).post('/api/sucursal-staff/', {
            'staff': vendedor2.id,
            'sucursal': self.sucursal.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        vendedor2 = create_vendedor(username='vendedor2')
        resp = auth_client(self.staff).post('/api/sucursal-staff/', {
            'staff': vendedor2.id,
            'sucursal': self.sucursal.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/sucursal-staff/{self.asignacion.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_duplicate_staff_sucursal(self):
        resp = auth_client(self.staff).post('/api/sucursal-staff/', {
            'staff': self.vendedor.id,
            'sucursal': self.sucursal.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class SucursalStaffFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))

        self.sucursal1 = Sucursal.objects.create(nombre='Norte', direccion='Calle 1', ciudad='Quito')
        self.sucursal2 = Sucursal.objects.create(nombre='Sur', direccion='Calle 2', ciudad='Guayaquil')

        vendedor1 = create_vendedor(username='v1', nombre='Pedro', apellido='Mena')
        vendedor2 = create_vendedor(username='v2', nombre='Sofia', apellido='Lopez')

        SucursalStaff.objects.create(staff=vendedor1, sucursal=self.sucursal1)
        SucursalStaff.objects.create(staff=vendedor2, sucursal=self.sucursal2)

    def test_filter_by_sucursal(self):
        resp = self.client.get(f'/api/sucursal-staff/?sucursal={self.sucursal2.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_search_by_staff_nombre(self):
        resp = self.client.get('/api/sucursal-staff/?search=pedro')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/sucursal-staff/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)