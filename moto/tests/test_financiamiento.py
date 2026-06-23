from django.test import TestCase
from rest_framework import status

from .helpers import (
    _generar_cedula,
    create_user,
    create_staff_user,
    auth_client,
    create_venta,
    create_cliente,
    create_vendedor,
    create_financiamiento,
)


class FinanciamientoPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.venta = create_venta()
        self.financiamiento = create_financiamiento(venta=self.venta)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/financiamientos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/financiamientos/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        cliente = create_cliente(cedula=_generar_cedula())
        vendedor = create_vendedor(username=f'staff_{_generar_cedula()}', cedula=_generar_cedula())
        venta = create_venta(cliente=cliente, vendedor=vendedor, total=5000)
        resp = auth_client(self.user).post('/api/financiamientos/', {
            'venta': venta.id,
            'monto_financiado': 5000,
            'tasa_interes': 5.0,
            'plazo_meses': 12,
            'fecha_inicio': '2026-01-15',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        cliente = create_cliente(cedula=_generar_cedula())
        vendedor = create_vendedor(username=f'staff_{_generar_cedula()}', cedula=_generar_cedula())
        venta = create_venta(cliente=cliente, vendedor=vendedor, total=5000)
        resp = auth_client(self.staff).post('/api/financiamientos/', {
            'venta': venta.id,
            'monto_financiado': 5000,
            'tasa_interes': 5.0,
            'plazo_meses': 12,
            'fecha_inicio': '2026-01-15',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/financiamientos/{self.financiamiento.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class FinanciamientoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        c1 = create_cliente(cedula=_generar_cedula())
        v1 = create_vendedor(username=f'ven_{_generar_cedula()}', cedula=_generar_cedula())
        c2 = create_cliente(cedula=_generar_cedula())
        v2 = create_vendedor(username=f'ven_{_generar_cedula()}', cedula=_generar_cedula())
        venta_1 = create_venta(cliente=c1, vendedor=v1, total=5000)
        venta_2 = create_venta(cliente=c2, vendedor=v2, total=8000)
        create_financiamiento(venta=venta_1, monto_financiado=5000, estado='activo')
        create_financiamiento(venta=venta_2, monto_financiado=8000, estado='pagado')

    def test_filter_by_estado(self):
        resp = self.client.get('/api/financiamientos/?estado=activo')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/financiamientos/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_registros', 'total_financiado', 'activos', 'pagados']:
            self.assertIn(field, resp.data)
