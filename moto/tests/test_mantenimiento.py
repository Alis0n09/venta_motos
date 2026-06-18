from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user,
    create_staff_user,
    auth_client,
    create_posventa,
    create_moto,
    create_mantenimiento,
)


class MantenimientoPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.posventa = create_posventa()
        self.moto = create_moto()
        self.mantenimiento = create_mantenimiento(
            posventa=self.posventa,
            moto=self.moto
        )

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/mantenimientos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/mantenimientos/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/mantenimientos/', {
            'posventa': self.posventa.id,
            'moto': self.moto.id,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': '2025-06-01',
            'descripcion': 'Cambio de aceite',
            'costo': 80.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        posventa = create_posventa()
        moto = create_moto()
        resp = auth_client(self.staff).post('/api/mantenimientos/', {
            'posventa': posventa.id,
            'moto': moto.id,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': '2025-06-01',
            'descripcion': 'Cambio de aceite',
            'costo': 80.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(
            f'/api/mantenimientos/{self.mantenimiento.id}/'
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class MantenimientoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        posventa_1 = create_posventa()
        posventa_2 = create_posventa()
        moto_1 = create_moto(marca='Honda')
        moto_2 = create_moto(marca='Yamaha')
        create_mantenimiento(
            posventa=posventa_1,
            moto=moto_1,
            tipo_mantenimiento='preventivo',
            costo=100.00,
            estado='pendiente'
        )
        create_mantenimiento(
            posventa=posventa_2,
            moto=moto_2,
            tipo_mantenimiento='correctivo',
            costo=250.00,
            estado='completado'
        )

    def test_filter_by_tipo_mantenimiento(self):
        resp = self.client.get('/api/mantenimientos/?tipo_mantenimiento=preventivo')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_estado(self):
        resp = self.client.get('/api/mantenimientos/?estado=completado')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_costo_min(self):
        resp = self.client.get('/api/mantenimientos/?costo_min=150')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/mantenimientos/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
