import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ReglaContrasenaSaboresValidator:
    # validador:
    #     -longitud entre 8 y 12 caracteres
    #     -alfanumerico obligatorio: solo permite letras y numeros

    def validate(self, password, user=None):
        if len(password) <8 or len(password) >12:
            raise ValidationError (
                _("La contrseña debe tener entre 8 y 12 caracteres."),
                code='longitud_invalida'
            )

        tiene_letras = bool(re.search(r'[a-zA-Z]', password))
        tiene_numeros = bool(re.search(r'[0-9]', password))

        if not (tiene_letras and tiene_numeros):
            raise ValidationError(
                _("La contraseña debe ser alfanimérica (no puede ser solo letras ni solo números)."),
                code='no_alfanumerica_mixta'
            )

        if not password.isalnum():
            raise ValidationError(
                _("La contraseña solo puede contener letras y números (sin espacios ni solo símbolos)."),
                code='carateres_no_permitidos'
            )

    def get_help_text(self):
        return _("Tu contraseña debe contener entre 8 y 12 caracteres y combinar letras y números")

class NoContieneNombreValidator:
    # validador para verficar que la contraseña no contega partes del nombre regitrado.
    def validate(self, password, user=None):
        if not user:
            return

        nombre = getattr(user, 'nombre', '') or getattr(user, 'first_name', '')
        if nombre:
            partes = [p.lower() for p in nombre.strip().split() if len(p) >= 3]
            pwd_lower = password.lower()
            for parte in partes:
                if parte in pwd_lower:
                    raise ValidationError(
                        _("Por seguridad, la contraseña no puede contener coincidencias con tu nombre."),
                        code='coincide_con_nombre'
                    )

    def get_help_text(self):
        return _("La contraseña no debe guardar coincidencias con el nombre ingresado.")