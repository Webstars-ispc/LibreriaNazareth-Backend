from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .lockout import (
    LOCKOUT_DURATION,
    MAX_FAILED_ATTEMPTS,
    check_lockout,
    register_failure,
    reset_failures,
)
from .models import LoginAttempt

LOGIN_URL = '/api/auth/login/'
REGISTER_URL = '/api/auth/register/'


class BaseThrottleTestCase(TestCase):
    def setUp(self):
        cache.clear()


class LoginThrottleTests(BaseThrottleTestCase):
    """Rate limiting del endpoint de login (scope 'login': 10/min)."""

    def test_login_returns_429_after_rate_exceeded(self):
        client = APIClient()
        payload = {'email': 'nadie@test.com', 'password': 'incorrecta'}

        for _ in range(10):
            response = client.post(LOGIN_URL, payload, format='json')
            # 400 = credenciales inválidas; 423 = se superó el umbral de bloqueo
            self.assertIn(response.status_code,
                          (status.HTTP_400_BAD_REQUEST, status.HTTP_423_LOCKED))

        response = client.post(LOGIN_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response)

    def test_register_returns_429_after_rate_exceeded(self):
        client = APIClient()
        payload = {'username': 'x', 'email': 'x@x.com', 'password': 'x'}

        for _ in range(5):
            client.post(REGISTER_URL, payload, format='json')

        response = client.post(REGISTER_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class AccountLockoutTests(BaseThrottleTestCase):
    """Bloqueo temporal por intentos fallidos de login (5 fallos -> 15 minutos)."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='claudia', email='claudia@test.com', password='secreta123'
        )
        self.client = APIClient()

    def _login(self, password='incorrecta'):
        return self.client.post(
            LOGIN_URL,
            {'email': 'claudia@test.com', 'password': password},
            format='json',
        )

    def test_four_failures_do_not_lock(self):
        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            response = self._login()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(check_lockout('claudia@test.com'), 0)

    def test_fifth_failure_locks_account(self):
        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            self._login()

        response = self._login()

        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertIn('Retry-After', response)
        retry_after = int(response.data['retry_after'])
        self.assertAlmostEqual(retry_after, int(LOCKOUT_DURATION.total_seconds()), delta=5)
        self.assertIn('bloqueada', response.data['message'])

        attempt = LoginAttempt.objects.get(email='claudia@test.com')
        self.assertTrue(attempt.is_locked())

    def test_locked_account_rejects_correct_password(self):
        for _ in range(MAX_FAILED_ATTEMPTS):
            self._login()

        response = self._login(password='secreta123')

        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)

    def test_successful_login_resets_failures(self):
        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            self._login()

        response = self._login(password='secreta123')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(LoginAttempt.objects.filter(email='claudia@test.com').exists())

        # El contador volvió a cero: hacen falta MAX_FAILED_ATTEMPTS fallos nuevos
        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            response = self._login()
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lock_expires_after_duration(self):
        for _ in range(MAX_FAILED_ATTEMPTS):
            self._login()

        attempt = LoginAttempt.objects.get(email='claudia@test.com')
        attempt.locked_until = timezone.now() - timedelta(seconds=1)
        attempt.save()

        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(check_lockout('claudia@test.com'), 0)

    def test_unknown_email_also_gets_locked(self):
        for _ in range(MAX_FAILED_ATTEMPTS):
            response = self.client.post(
                LOGIN_URL,
                {'email': 'hacker@test.com', 'password': 'probando'},
                format='json',
            )
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)


class LockoutHelperTests(BaseThrottleTestCase):
    def test_check_lockout_returns_zero_for_new_email(self):
        self.assertEqual(check_lockout('nuevo@test.com'), 0)

    def test_register_failure_counts_up_to_lock(self):
        for i in range(1, MAX_FAILED_ATTEMPTS):
            self.assertEqual(register_failure('algo@test.com'), 0)
            attempt = LoginAttempt.objects.get(email='algo@test.com')
            self.assertEqual(attempt.failed_attempts, i)

        locked_for = register_failure('algo@test.com')
        self.assertEqual(locked_for, int(LOCKOUT_DURATION.total_seconds()))
        attempt = LoginAttempt.objects.get(email='algo@test.com')
        self.assertTrue(attempt.is_locked())
        self.assertEqual(check_lockout('algo@test.com'), locked_for)

    def test_reset_failures_clears_state(self):
        register_failure('algo@test.com')
        reset_failures('algo@test.com')
        self.assertFalse(LoginAttempt.objects.filter(email='algo@test.com').exists())
        self.assertEqual(check_lockout('algo@test.com'), 0)

    def test_email_is_normalized(self):
        register_failure('  Mixta@Test.COM ')
        self.assertTrue(LoginAttempt.objects.filter(email='mixta@test.com').exists())
        self.assertEqual(check_lockout('MIXTA@test.com'), 0)
        class AdminUserEditSecurityTests(TestCase):
          """Verifica que la API no permita editar usuarios."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_seguridad',
            email='admin_seguridad@test.com',
            password='AdminTest123!'
        )
        self.employee = User.objects.create_user(
            username='empleado_prueba',
            email='empleado_prueba@test.com',
            password='EmpleadoTest123!'
        )

        # El permiso IsAdminUser del proyecto exige pertenecer
        # al grupo Administrador.
        from django.contrib.auth.models import Group
        grupo_admin, _ = Group.objects.get_or_create(name='Administrador')
        self.admin.groups.add(grupo_admin)

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_put_user_is_rejected(self):
        response = self.client.put(
            '/api/auth/usuarios/{}/'.format(self.employee.pk),
            {
                'username': 'empleado_modificado',
                'email': 'empleado_prueba@test.com',
                'password': 'OtraClave123!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.username, 'empleado_prueba')

    def test_patch_user_is_rejected(self):
        response = self.client.patch(
            '/api/auth/usuarios/{}/'.format(self.employee.pk),
            {'username': 'empleado_modificado'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.username, 'empleado_prueba')