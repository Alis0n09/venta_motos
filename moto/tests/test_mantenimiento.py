from django.test import TestCase
from rest_framework import status

from .helpers import (
    _generar_cedula,
    create_user,
    create_staff_user,
    auth_client,
    create_moto,
    create_cliente,
    create_mantenimiento,
)


class MantenimientoPermissionTests(TestCase):

    def setUp(self):
        self.user = create_user('eve')
        self.staff = create_staff_user()
        self.moto = create_moto()
        self.cliente = create_cliente(cedula=_generar_cedula())
        self.mantenimiento = create_mantenimiento(moto=self.moto, cliente=self.cliente)

    def test_authenticated_user_can_list(self):
        resp = auth_client(self.user).get('/api/mantenimientos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        from rest_framework.test import APIClient
        resp = APIClient().get('/api/mantenimientos/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create(self):
        moto = create_moto()
        cliente = create_cliente(cedula=_generar_cedula())
        resp = auth_client(self.user).post('/api/mantenimientos/', {
            'moto': moto.id,
            'cliente': cliente.id,
            'fecha': '2026-06-15',
            'tipo': 'preventivo',
            'costo': 150.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create(self):
        moto = create_moto()
        cliente = create_cliente(cedula=_generar_cedula())
        resp = auth_client(self.staff).post('/api/mantenimientos/', {
            'moto': moto.id,
            'cliente': cliente.id,
            'fecha': '2026-06-15',
            'tipo': 'preventivo',
            'costo': 150.00,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_staff_can_delete(self):
        resp = auth_client(self.staff).delete(f'/api/mantenimientos/{self.mantenimiento.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class MantenimientoFilterTests(TestCase):

    def setUp(self):
        self.client = auth_client(create_user('filters'))
        moto_1 = create_moto(modelo='CBR 500R', color='Rojo')
        moto_2 = create_moto(modelo='MT-07', color='Azul')
        c1 = create_cliente(cedula=_generar_cedula())
        c2 = create_cliente(cedula=_generar_cedula())
        create_mantenimiento(moto=moto_1, cliente=c1, tipo='preventivo')
        create_mantenimiento(moto=moto_2, cliente=c2, tipo='correctivo')

    def test_filter_by_tipo(self):
        resp = self.client.get('/api/mantenimientos/?tipo=preventivo')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 1)

    def test_stats_returns_expected_fields(self):
        resp = self.client.get('/api/mantenimientos/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for field in ['total_registros', 'total_gastado']:
            self.assertIn(field, resp.data)
