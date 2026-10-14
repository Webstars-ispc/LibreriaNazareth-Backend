
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Rubro


class RubroPruebas(APITestCase):
    def test_crear_rubro(self):
        """Verifica que se puede crear un rubro y devuelve 201."""
        User = get_user_model()
        user = User.objects.create_user(
            username='test_admin',
            email='test_admin@test.com',
            password='Test12345!'
        )
        self.client.force_authenticate(user=user)

        url = '/api/rubros/'
        data = {'nombre': 'Papelería'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rubro.objects.count(), 1)
        self.assertEqual(Rubro.objects.get().nombre, 'Papelería')

    def test_obtener_rubros(self):
        """Verifica que la lista de rubros devuelve 200."""
        User = get_user_model()
        user = User.objects.create_user(
            username='test_rubros',
            email='test_rubros@test.com',
            password='Test12345!'
        )
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/rubros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
