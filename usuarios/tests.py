from django.test import TestCase
from usuarios.forms import RegistroClienteForm


class RegistroClienteFormTests(TestCase):
    def test_password_validator_is_applied(self):
        data = {
            'nombre': 'Ana',
            'apellido': 'Pérez',
            'email': 'ana.validacion@sabores.cl',
            'telefono': '+56912345678',
            'empresa_convenio': '',
            'calle_y_numero': 'Calle 123',
            'comuna': 'Santiago',
            'password': 'ana',
            'confirmar_password': 'ana',
        }

        form = RegistroClienteForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
