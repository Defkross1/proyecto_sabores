from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'GERENTE')
        return self.create_user(email, nombre, password, **extra_fields)

class EmpresaConvenio(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre Empresa")
    rut = models.CharField(max_length=15, unique=True, verbose_name="RUT Empresa")
    direccion = models.CharField(max_length=255, verbose_name="Dirección Comercial")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (RUT: {self.rut})"

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('GERENTE', 'Gerente'),
        ('ATENCION', 'Atención al cliente'),
        ('REPARTIDOR', 'Repartidor'),
        ('CLIENTE', 'Cliente'),
    ]

    email = models.EmailField(unique=True, db_index=True, verbose_name="Correo Electrónico")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido")
    rut = models.CharField(max_length=15, blank=True, null=True, unique=True, verbose_name="Rut")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    cargo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo")
    rol = models.CharField(max_length=20, choices=ROLES, default='CLIENTE', verbose_name="Rol en el Sistema")

    empresa_convenio = models.ForeignKey(
        EmpresaConvenio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="afiliados",
        verbose_name="Empresa en Convenio"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']
    EMAIL_FIELD = 'email'

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''} ({self.get_rol_display()})"

class DireccionCliente(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="direcciones")
    calle_y_numero = models.CharField(max_length=255, verbose_name="Calle y Número")
    comuna = models.CharField(max_length=100, verbose_name="Comuna")
    departamento_oficina = models.CharField(max_length=50, blank=True, null=True, verbose_name="Depto / Oficina")
    es_principal = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.cliente.direcciones.count() <= 1:
            raise ValidationError("Debe mantener al menos una dirección registrada en su cuenta.")
        super().delete(*args, **kwargs)

    def __str__(self):
        depto = f" - depto {self.departamento_oficina}" if self.departamento_oficina else ""
        return f"{self.calle_y_numero}{depto}, {self.comuna}"
