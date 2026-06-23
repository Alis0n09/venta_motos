from django.test import TestCase
from rest_framework import status

from .helpers import (
    create_user,
    create_staff_user,
    auth_client,
    create_financiamiento,
    create_cuota_pago,
)


class CuotaPagoPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.financiamiento = create_financiamiento()
        self.cuota = create_cuota_pago(financiamiento=self.financiamiento)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/cuotas-pago/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/cuotas-pago/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        from .helpers import create_financiamiento
        otro_financiamiento = create_financiamiento()
        resp = auth_client(self.user).post('/api/cuotas-pago/', {
            'financiamiento': otro_financiamiento.id,
            'numero_cuota': 1,
            'fecha_vencimiento': '2026-02-15',
            'monto': 500.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        resp = auth_client(self.staff).post('/api/cuotas-pago/', {
            'financiamiento': self.financiamiento.id,
            'numero_cuota': 2,
            'fecha_vencimiento': '2026-03-15',
            'monto': 500.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/cuotas-pago/{self.cuota.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class CuotaPagoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        f1 = create_financiamiento()
        f2 = create_financiamiento()
        create_cuota_pago(financiamiento=f1, numero_cuota=1, monto=500, estado='pendiente')
        create_cuota_pago(financiamiento=f2, numero_cuota=1, monto=800, estado='pagada')

    def test_filter_by_estado(self):
        resp = self.client.get('/api/cuotas-pago/?estado=pagada')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/cuotas-pago/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_registros', 'pagadas', 'pendientes', 'vencidas', 'total_pagado', 'total_pendiente']:
            self.assertIn(field, resp.data)
