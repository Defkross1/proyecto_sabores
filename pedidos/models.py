from django.conf import settings
from django.db import models

from usuarios.models import DireccionCliente


class Proveedores(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre o Razón Social")
    contacto = models.CharField(max_length=120, verbose_name="Persona de Contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PlatoMenu(models.Model):
    DIAS = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
    ]

    nombre = models.CharField(max_length=150, verbose_name="Nombre del Plato")
    descripcion = models.TextField(verbose_name="Descripción del Plato")
    dia_semana = models.CharField(max_length=12, choices=DIAS, verbose_name="Día Asignado")
    precio = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio")
    proveedor = models.ForeignKey(Proveedores, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_dia_semana_display()}] {self.nombre}"


class Pedidos(models.Model):
    ESTADO = [
        ('SOLICITADO', 'Solicitado por App Web'),
        ('EN_PREPARACION', 'En Preparación'),
        ('EN_RUTA', 'En Ruta'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    ESTADOS = ESTADO
    HORARIOS_ENTREGA = [
        ('12:00 - 13:00', '12:00 a 13:00 Hrs'),
        ('13:00 - 14:00', '13:00 a 14:00 Hrs'),
        ('14:00 - 15:00', '14:00 a 15:00 Hrs'),
    ]

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos")
    direccion = models.ForeignKey(DireccionCliente, on_delete=models.PROTECT, verbose_name="Dirección de Entrega")
    horario_entrega = models.CharField(max_length=30, choices=HORARIOS_ENTREGA)
    estado = models.CharField(max_length=25, choices=ESTADO, default='SOLICITADO')
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_asignados"
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def recalculador_total(self):
        subtotales = [item.cantidad * item.precio_unitario for item in self.items.all()]
        self.total = sum(subtotales)
        self.save()
        return self.total

    def recalcular_total(self):
        return self.recalculador_total()

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nombre} ({self.get_estado_display()})"


class ItemPedido(models.Model):
    OPCIONES_ACOMPANAMIENTO = [
        ('ENSALADA', 'Ensalada'),
        ('CONSOME', 'Consomé'),
        ('NINGUNO', 'Sin acompañamiento'),
    ]

    pedido = models.ForeignKey(Pedidos, related_name="items", on_delete=models.CASCADE)
    plato = models.ForeignKey(PlatoMenu, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    acompanamiento = models.CharField(max_length=20, choices=OPCIONES_ACOMPANAMIENTO, default='NINGUNO', verbose_name="Acompañamiento")

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.plato.precio
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


Proveedor = Proveedores
Pedido = Pedidos


