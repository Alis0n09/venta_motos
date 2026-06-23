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
    create_garantia,
)


class GarantiaPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.venta = create_venta()
        self.garantia = create_garantia(venta=self.venta)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/garantias/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/garantias/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        cliente = create_cliente(cedula=_generar_cedula())
        vendedor = create_vendedor(username=f'ven_{_generar_cedula()}', cedula=_generar_cedula())
        venta = create_venta(cliente=cliente, vendedor=vendedor)
        resp = auth_client(self.user).post('/api/garantias/', {
            'venta': venta.id,
            'fecha_inicio': '2026-01-01',
            'fecha_fin': '2027-01-01',
            'tipo': 'Cobertura completa',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        cliente = create_cliente(cedula=_generar_cedula())
        vendedor = create_vendedor(username=f'staff_{_generar_cedula()}', cedula=_generar_cedula())
        venta = create_venta(cliente=cliente, vendedor=vendedor)
        resp = auth_client(self.staff).post('/api/garantias/', {
            'venta': venta.id,
            'fecha_inicio': '2026-01-01',
            'fecha_fin': '2027-01-01',
            'tipo': 'Cobertura completa',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/garantias/{self.garantia.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class GarantiaFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        c1 = create_cliente(cedula=_generar_cedula())
        v1 = create_vendedor(username=f'ven_{_generar_cedula()}', cedula=_generar_cedula())
        c2 = create_cliente(cedula=_generar_cedula())
        v2 = create_vendedor(username=f'ven_{_generar_cedula()}', cedula=_generar_cedula())
        venta_1 = create_venta(cliente=c1, vendedor=v1)
        venta_2 = create_venta(cliente=c2, vendedor=v2)
        create_garantia(venta=venta_1, tipo='Cobertura completa')
        create_garantia(venta=venta_2, tipo='Cobertura parcial')

    def test_filter_by_tipo(self):
        resp = self.client.get('/api/garantias/?tipo=Cobertura completa')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/garantias/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_registros', resp.data)
