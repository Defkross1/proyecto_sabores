from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Usuario, DireccionCliente, EmpresaConvenio
from .validators import ReglaContrasenaSaboresValidator, NoContieneNombreValidator

class RegistroClienteForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '8 a 12 alfanumerico'})   
    )
    confirmar_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    calle_y_numero = forms.CharField(
        label="Dirección (Calle y Número)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Los carrera 1234'})
    )
    comuna = forms.CharField(
        label="Comuna",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Quilpué'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'nombre' : forms.TextInput(attrs={'class': 'form-control'}),
            'apellido' : forms.TextInput(attrs={'class' : 'form-control'}),
            'email' : forms.EmailInput(attrs={'class' : 'form-control'}),
            'telefono' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Ej: +56912345678'}),
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        nombre = self.cleaned_data.get('nombre')

        if not pwd:
            return pwd

        validador_regla = ReglaContrasenaSaboresValidator()
        validador_regla.validate(pwd)

        temp_user = Usuario(nombre=nombre)
        validator_nombre = NoContieneNombreValidator()
        validator_nombre.validate(pwd, user=temp_user)

        return pwd

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirmar_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.rol = 'CLIENTE'
        if commit:
            user.save()
            DireccionCliente.objects.create(
                cliente=user,
                calle_y_numero=self.cleaned_data['calle_y_numero'],
                comuna=self.cleaned_data['comuna'],
                es_principal=True
            )
        return user


class RegistroEmpresaConvenioForm(forms.ModelForm):
    rut_empresa = forms.CharField(
        label="RUT de la Empresa",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.123.456-7'})
    )
    clave_empresa = forms.CharField(
        label="Clave de Convenio de la Empresa",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Clave secreta corporativa'})
    )
    password = forms.CharField(
        label="Tu Contraseña Personal",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_password = forms.CharField(
        label="Confirmar Tu Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'email', 'rut', 'telefono', 'empresa_convenio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu RUT personal'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa_convenio': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        empresa = cleaned_data.get('empresa_convenio')
        rut_ingresado = cleaned_data.get('rut_empresa')
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirmar_password')

        if p1 and p2 and p1 != p2:
            self.add_error('confirmar_password', "Las contraseñas no coinciden.")

        if empresa and rut_ingresado:
            if empresa.rut.strip().lower() != rut_ingresado.strip().lower():
                self.add_error('rut_empresa', "El RUT ingresado no coincide con el RUT registrado para esta empresa en convenio.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.rol = 'CLIENTE'
        if commit:
            user.save()
            DireccionCliente.objects.create(
                cliente=user,
                calle_y_numero=user.empresa_convenio.direccion if user.empresa_convenio else "Dirección Principal",
                comuna="Santiago",
                es_principal=True
            )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@dominio.cl'}) 
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user :
                raise forms.ValidationError("Credenciales inválidas. Revisa el correo y contraseña.")
            self.user_cache = user
        return cleaned_data

class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = ['calle_y_numero', 'departamento_oficina', 'comuna']
        widgets = {
            'calle_y_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento_oficina': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
        }

DireccionForm = DireccionClienteForm