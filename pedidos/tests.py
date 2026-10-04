from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario


class ClienteFlowTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='cliente.flow@sabores.cl',
            nombre='Cliente',
            apellido='Flow',
            password='Cliente123',
            rol='CLIENTE',
        )

    def test_client_can_access_main_client_views(self):
        self.client.login(email='cliente.flow@sabores.cl', password='Cliente123')

        self.assertEqual(self.client.get(reverse('menu_semanal')).status_code, 200)
        self.assertEqual(self.client.get(reverse('mis_pedidos')).status_code, 200)
        self.assertEqual(self.client.get(reverse('perfil_cliente')).status_code, 200)
