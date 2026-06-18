from datetime import date
from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user,
    create_staff_user,
    auth_client,
    create_posventa,
    create_garantia,
)


class GarantiaPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.posventa = create_posventa()
        self.garantia = create_garantia(posventa=self.posventa)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/garantias/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/garantias/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        resp = auth_client(self.user).post('/api/garantias/', {
            'posventa': self.posventa.id,
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2026-01-01',
            'tipo_cobertura': 'Básica',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        posventa = create_posventa()
        resp = auth_client(self.staff).post('/api/garantias/', {
            'posventa': posventa.id,
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2026-01-01',
            'tipo_cobertura': 'Básica',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/garantias/{self.garantia.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class GarantiaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        posventa_1 = create_posventa()
        posventa_2 = create_posventa()
        create_garantia(
            posventa=posventa_1,
            tipo_cobertura='Cobertura completa',
            estado='activa'
        )
        create_garantia(
            posventa=posventa_2,
            tipo_cobertura='Cobertura parcial',
            estado='expirada'
        )

    def test_filter_by_estado(self):
        resp = self.client.get('/api/garantias/?estado=activa')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_tipo_cobertura(self):
        resp = self.client.get('/api/garantias/?tipo_cobertura=completa')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/garantias/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total', 'detail']:
            self.assertIn(field, resp.data)
