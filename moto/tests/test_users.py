# moto/tests/test_users.py

from django.test import TestCase
from rest_framework import status
from django.test import override_settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from .helpers import create_user, create_staff_user, auth_client


class ProfileTests(TestCase):

    def setUp(self):
        self.user   = create_user('carlos')
        self.client = auth_client(self.user)

    def test_get_own_profile(self):
        resp = self.client.get('/api/users/profile/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'carlos')

    def test_update_own_profile(self):
        resp = self.client.patch('/api/users/profile/', {
            'first_name': 'Carlos'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['first_name'], 'Carlos')

    def test_change_password_success(self):
        resp = self.client.post('/api/users/change-password/', {
            'current_password': 'Pass1234!',
            'new_password':     'New5678!',
            'new_password2':    'New5678!',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_current(self):
        resp = self.client.post('/api/users/change-password/', {
            'current_password': 'Wrong!',
            'new_password':     'New5678!',
            'new_password2':    'New5678!',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class UserStaffTests(TestCase):

    def setUp(self):
        self.staff  = create_staff_user()
        self.user   = create_user('diana')
        self.client = auth_client(self.staff)

    def test_staff_can_list_users(self):
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)

    def test_regular_user_cannot_list(self):
        resp = auth_client(self.user).get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_toggle_active(self):
        resp = self.client.post(f'/api/users/{self.user.id}/toggle-active/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', resp.data)

    def test_staff_can_get_stats(self):
        resp = self.client.get('/api/users/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for field in ['total', 'active', 'inactive', 'staff']:
            self.assertIn(field, resp.data)

    def test_filter_by_is_staff(self):
        resp = self.client.get('/api/users/?is_staff=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        for user in resp.data['results']:
            self.assertTrue(user['is_staff'])

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):

    def setUp(self):
        self.user = create_user('resetme')

    def test_solicitar_reset_usuario_existente(self):
        resp = self.client.post('/api/auth/password-reset/', {
            'username': 'resetme',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Confirma que sí se "envió" un correo (capturado por el backend falso)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('resetme', mail.outbox[0].to[0] if False else mail.outbox[0].body)

    def test_solicitar_reset_usuario_inexistente(self):
        resp = self.client.post('/api/auth/password-reset/', {
            'username': 'noexiste123',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_reset_exitoso(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        codigo = f"{uid}.{token}"

        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'codigo': codigo,
            'new_password': 'NuevaClave123',
            'new_password2': 'NuevaClave123',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Confirma que la contraseña realmente cambió, haciendo login con la nueva
        login_resp = self.client.post('/api/auth/login/', {
            'username': 'resetme',
            'password': 'NuevaClave123',
        })
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    def test_confirmar_reset_codigo_invalido(self):
        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'codigo': 'basura.invalida',
            'new_password': 'NuevaClave123',
            'new_password2': 'NuevaClave123',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirmar_reset_passwords_no_coinciden(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        codigo = f"{uid}.{token}"

        resp = self.client.post('/api/auth/password-reset/confirm/', {
            'codigo': codigo,
            'new_password': 'NuevaClave123',
            'new_password2': 'OtraDistinta456',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)