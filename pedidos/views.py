from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime, timedelta
import zoneinfo
from .models import PlatoMenu, Proveedor, Pedido, ItemPedido
from usuarios.models import Usuario, EmpresaConvenio, DireccionCliente
from usuarios.decorators import rol_requerido

# ==================== VISTA PORTADA E INICIO ====================
@require_http_methods(["GET"])
def portada_view(request):
    platos_destacados = [
        {'id': 1, 'nombre': 'Cazuela', 'descripcion': 'Tradicional cazuela casera con presa de carne o pollo, choclo, zapallo y papas.', 'precio': '6.500', 'imagen': 'images/platos/cazuela.jpg'},
        {'id': 2, 'nombre': 'Pollo Arvejado', 'descripcion': 'Jugoso pollo en salsa arvejada acompañado de arroz graneado.', 'precio': '6.000', 'imagen': 'images/platos/pollo_arvejado.jpg'},
        {'id': 3, 'nombre': 'Pollo con Ensalada', 'descripcion': 'Pechuga de pollo a la plancha jugosa acompañada de ensalada fresca del día.', 'precio': '5.800', 'imagen': 'images/platos/pollo_con_ensalada.jpg'},
        {'id': 4, 'nombre': 'Pescado Frito con Puré', 'descripcion': 'Filete de pescado frito dorado y crujiente con suave puré de papas casero.', 'precio': '7.500', 'imagen': 'images/platos/Pescado_Frito_con_Pure.jpg'},
        {'id': 5, 'nombre': 'Porotos con Rienda', 'descripcion': 'Deliciosos porotos tradicionales con fideos y zapallo al estilo casero.', 'precio': '5.500', 'imagen': 'images/platos/Porotos_con_rienda.jpg'},
        {'id': 6, 'nombre': 'Bistec a lo Pobre', 'descripcion': 'Abundante bistec de vacuno con papas fritas crujientes, cebolla caramelizada y huevo frito.', 'precio': '9.500', 'imagen': 'images/platos/Bistec_a_lo_Pobre.jpg'},
        {'id': 7, 'nombre': 'Ensalada César', 'descripcion': 'Lechuga romana crujiente, crutones dorados, queso parmesano, pollo a la plancha y aderezo césar.', 'precio': '5.000', 'imagen': 'images/platos/Ensalada_Cesar.jpg'},
    ]

    chefs = [
        {'nombre': 'Geovanni Huerta', 'especialidad': 'Comida Tradicional Chilena', 'imagen': 'images/chefs/geovanni_huerta.jpg'},
        {'nombre': 'Jeanliette muñoz', 'especialidad': 'Masas y Repostería Casera', 'imagen': 'images/chefs/Jeanliette_muñoz.jpg'},
        {'nombre': 'Jonathan Quiroz', 'especialidad': 'Carnes y Platos a la Parrilla', 'imagen': 'images/chefs/jonathan_quiroz.jpg'},
        {'nombre': 'Andres Molina', 'especialidad': 'Ensaladas y Comida Saludable', 'imagen': 'images/chefs/andres_molina.jpg'},
    ]

    return render(request, 'pedidos/portada.html', {'platos': platos_destacados, 'chefs': chefs})


# ==================== VISTA CARRITO / PEDIDO DESDE PORTADA ====================
@require_http_methods(["GET", "POST"])
def carrito_pedido_view(request):
    empresas = EmpresaConvenio.objects.all()
    plato_seleccionado = None
    plato_index = request.GET.get('plato')
    
    platos_lista = [
        {'nombre': 'Cazuela', 'precio': '6.500'},
        {'nombre': 'Pollo Arvejado', 'precio': '6.000'},
        {'nombre': 'Pollo con Ensalada', 'precio': '5.800'},
        {'nombre': 'Pescado Frito con Puré', 'precio': '7.500'},
        {'nombre': 'Porotos con Rienda', 'precio': '5.500'},
        {'nombre': 'Bistec a lo Pobre', 'precio': '9.500'},
        {'nombre': 'Ensalada César', 'precio': '5.000'},
    ]

    if plato_index and plato_index.isdigit():
        idx = int(plato_index) - 1
        if 0 <= idx < len(platos_lista):
            plato_seleccionado = platos_lista[idx]

    if request.user.is_authenticated and plato_seleccionado:
        plato_obj, created = PlatoMenu.objects.get_or_create(
            nombre=plato_seleccionado['nombre'],
            defaults={
                'descripcion': 'Plato seleccionado desde la portada principal.',
                'precio': float(plato_seleccionado['precio'].replace('.', '')),
                'dia_semana': 'LUNES',
                'activo': True
            }
        )

        try:
            direccion_bd = None
            if hasattr(request.user, 'direcciones') and request.user.direcciones.exists():
                direccion_bd = request.user.direcciones.first()
            elif DireccionCliente.objects.filter(cliente=request.user).exists():
                direccion_bd = DireccionCliente.objects.filter(cliente=request.user).first()
            else:
                dir_texto = f"{request.user.empresa_convenio.nombre}\n{request.user.empresa_convenio.direccion}" if hasattr(request.user, 'empresa_convenio') and request.user.empresa_convenio else "Dirección Principal"
                direccion_bd = DireccionCliente.objects.create(
                    cliente=request.user,
                    calle_y_numero=dir_texto,
                    comuna="Santiago"
                )

            pedido, created_pedido = Pedido.objects.get_or_create(
                cliente=request.user,
                estado='SOLICITADO',
                defaults={
                    'direccion': direccion_bd,
                    'horario_entrega': "12:00 - 13:00"
                }
            )

            item, created_item = ItemPedido.objects.get_or_create(
                pedido=pedido,
                plato=plato_obj,
                defaults={
                    'cantidad': 1,
                    'precio_unitario': plato_obj.precio,
                    'acompanamiento': 'NINGUNO'
                }
            )
            
            if not created_item:
                item.cantidad += 1
                item.save()

            pedido.recalcular_total()
            messages.success(request, f"¡'{plato_obj.nombre}' se ha sumado a tu pedido unificado!")
            return redirect('mis_pedidos')
        except Exception as e:
            messages.error(request, f"Error de seguridad al procesar el plato: {e}")
            return redirect('portada')

    elif request.user.is_authenticated:
        return redirect('menu_semanal')

    if request.method == 'POST':
        rut_trabajador = request.POST.get('rut', '').strip()
        clave = request.POST.get('clave', '')
        empresa_id = request.POST.get('empresa_id')

        if not rut_trabajador or not clave or not empresa_id:
            messages.error(request, "Todos los campos son obligatorios para validar el convenio.")
            return redirect('carrito_pedido')

        try:
            usuario = Usuario.objects.get(rut=rut_trabajador, empresa_convenio_id=empresa_id)
            user_auth = authenticate(request, username=usuario.email, password=clave)
            
            if user_auth is not None:
                request.session.cycle_key()
                login(request, user_auth)
                messages.success(request, f"¡Bienvenido, {usuario.nombre}! Autenticado de forma segura por convenio.")
                if plato_seleccionado:
                    return redirect(f"{request.path}?plato={plato_index}")
                return redirect('menu_semanal')
            else:
                messages.error(request, "Credenciales inválidas. Verifique su RUT y clave de acceso.")
        except Usuario.DoesNotExist:
            messages.error(request, "No existe un trabajador registrado con ese RUT en la empresa seleccionada.")

    return render(request, 'pedidos/carrito.html', {'empresas': empresas, 'plato': plato_seleccionado})


# ==================== VISTA MENÚ SEMANAL ====================
@login_required
def menu_semanal_cliente(request):
    chile_tz = zoneinfo.ZoneInfo('America/Santiago')
    now_chile = datetime.now(chile_tz)
    
    start_of_week = now_chile.date() - timedelta(days=now_chile.weekday())
    
    dias_semana_info = [
        {'clave': 'LUNES', 'nombre': 'Lunes', 'fecha': start_of_week + timedelta(days=0)},
        {'clave': 'MARTES', 'nombre': 'Martes', 'fecha': start_of_week + timedelta(days=1)},
        {'clave': 'MIERCOLES', 'nombre': 'Miércoles', 'fecha': start_of_week + timedelta(days=2)},
        {'clave': 'JUEVES', 'nombre': 'Jueves', 'fecha': start_of_week + timedelta(days=3)},
        {'clave': 'VIERNES', 'nombre': 'Viernes', 'fecha': start_of_week + timedelta(days=4)},
    ]
    
    menus_por_dia = {}
    dias_habilitados = {}
    fechas_dias = {}

    for item in dias_semana_info:
        dia = item['clave']
        fechas_dias[dia] = item['fecha']
        
        platos = PlatoMenu.objects.filter(dia_semana=dia, activo=True)
        if not platos.exists():
            platos = PlatoMenu.objects.filter(activo=True)
        menus_por_dia[dia] = platos
        
        dias_habilitados[dia] = True

    class DiasEstado:
        pass
    estado_dias = DiasEstado()
    for d, val in dias_habilitados.items():
        setattr(estado_dias, d, val)

    direcciones = list(DireccionCliente.objects.filter(cliente=request.user))
    if hasattr(request.user, 'empresa_convenio') and request.user.empresa_convenio:
        emp = request.user.empresa_convenio
        class DireccionEmpresaConvenio:
            def __init__(self, emp_id, texto_dir, nombre_emp):
                self.id = f"empresa_{emp_id}"
                self.direccion = f"{nombre_emp} ({texto_dir})"
            def __str__(self):
                return self.direccion
        direcciones.insert(0, DireccionEmpresaConvenio(emp.id, emp.direccion, emp.nombre))

    if request.method == 'POST':
        dir_id = request.POST.get('direccion')
        horario = request.POST.get('horario_entrega')

        if not dir_id or not horario:
            messages.error(request, "Debes seleccionar una dirección y un horario de entrega.")
            return redirect('menu_semanal')

        try:
            direccion_bd = None
            if str(dir_id).startswith("empresa_") and hasattr(request.user, 'empresa_convenio'):
                emp = request.user.empresa_convenio
                direccion_bd, _ = DireccionCliente.objects.get_or_create(
                    cliente=request.user,
                    defaults={
                        'calle_y_numero': f"{emp.nombre}\n{emp.direccion}",
                        'comuna': "Santiago"
                    }
                )
            else:
                direccion_bd = DireccionCliente.objects.filter(id=dir_id, cliente=request.user).first()
                if not direccion_bd:
                    direccion_bd = DireccionCliente.objects.filter(cliente=request.user).first()

            if not direccion_bd:
                direccion_bd = DireccionCliente.objects.create(
                    cliente=request.user,
                    calle_y_numero="Dirección Principal",
                    comuna="Santiago"
                )

            pedido, created_pedido = Pedido.objects.get_or_create(
                cliente=request.user,
                estado='SOLICITADO',
                defaults={
                    'direccion': direccion_bd,
                    'horario_entrega': horario
                }
            )

            seleccion_realizada = False
            dias_keys = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES']
            for dia in dias_keys:
                platos_ids = request.POST.getlist(f'plato_{dia}')
                for plato_id in platos_ids:
                    if plato_id:
                        try:
                            plato = PlatoMenu.objects.get(id=plato_id)
                            acompanamiento = request.POST.get(f'acompanamiento_{dia}_{plato_id}', 'NINGUNO')
                            
                            item, created_item = ItemPedido.objects.get_or_create(
                                pedido=pedido,
                                plato=plato,
                                defaults={
                                    'cantidad': 1,
                                    'precio_unitario': plato.precio,
                                    'acompanamiento': acompanamiento
                                }
                            )
                            if not created_item:
                                item.cantidad += 1
                                item.acompanamiento = acompanamiento
                                item.save()

                            seleccion_realizada = True
                        except PlatoMenu.DoesNotExist:
                            pass

            if not seleccion_realizada:
                messages.error(request, "Debes seleccionar al menos un plato válido.")
                return redirect('menu_semanal')

            pedido.recalcular_total()
            messages.success(request, f"¡Pedido unificado #{pedido.id} actualizado con éxito!")
            return redirect('mis_pedidos')

        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pedido: {e}")
            return redirect('menu_semanal')

    return render(request, 'pedidos/menu_semanal.html', {
        'menus_por_dia': menus_por_dia,
        'dias_habilitados': dias_habilitados,
        'estado_dias': estado_dias,
        'fechas_dias': fechas_dias,
        'direcciones': direcciones,
        'horarios': Pedido.HORARIOS_ENTREGA,
    })


@login_required
def mis_pedidos(request):
    pedidos = request.user.pedidos.all().order_by('-fecha_pedido')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def boleta_pedido(request, pedido_id):
    if request.user.rol in ['GERENTE', 'ATENCION']:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    if not pedido.pagado and request.user.rol not in ['GERENTE', 'ATENCION']:
        messages.error(request, "Debes pagar el pedido antes de ver la boleta.")
        return redirect('mis_pedidos')

    return render(request, 'pedidos/boleta.html', {'pedido': pedido})


@login_required
def pagar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago')
        if metodo:
            # LÓGICA DE DESCUENTO PARA LA GIFT CARD DE CONVENIO
            if metodo == 'GIFTCARD':
                if hasattr(request.user, 'saldo_giftcard') and request.user.saldo_giftcard >= pedido.total:
                    request.user.saldo_giftcard -= pedido.total
                    request.user.save()
                    messages.success(request, f"Se ha descontado ${pedido.total} de tu Gift Card.")
                else:
                    messages.error(request, "Saldo insuficiente en tu Gift Card de Convenio.")
                    return redirect('mis_pedidos')

            pedido.metodo_pago = metodo
            pedido.pagado = True
            pedido.estado = 'EN_PREPARACION'
            pedido.save()
            messages.success(request, "¡Pago registrado con éxito! Tu boleta ya está disponible.")
        else:
            messages.error(request, "Debes seleccionar un método de pago.")
    return redirect('mis_pedidos')


@login_required
def eliminar_pedido_cliente(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if pedido.estado == 'SOLICITADO' and not pedido.pagado:
        pedido.delete()
        messages.success(request, f"El pedido #{pedido_id} ha sido eliminado con éxito.")
    else:
        messages.error(request, "No se puede eliminar un pedido que ya está pagado o en proceso.")
    return redirect('mis_pedidos')


@login_required
def editar_pedido_cliente(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if pedido.estado != 'SOLICITADO' or pedido.pagado:
        messages.error(request, "Este pedido ya no se puede editar.")
        return redirect('mis_pedidos')

    platos_disponibles = PlatoMenu.objects.filter(activo=True)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                pedido.items.all().delete()
                seleccion_realizada = False
                
                for plato in platos_disponibles:
                    plato_id_str = str(plato.id)
                    if request.POST.get(f'seleccionar_{plato_id_str}'):
                        acompanamiento = request.POST.get(f'acompanamiento_{plato_id_str}', 'NINGUNO')
                        ItemPedido.objects.create(
                            pedido=pedido,
                            plato=plato,
                            cantidad=1,
                            precio_unitario=plato.precio,
                            acompanamiento=acompanamiento
                        )
                        seleccion_realizada = True

                if not seleccion_realizada:
                    transaction.set_rollback(True)
                    messages.error(request, "Debes seleccionar al menos un plato para actualizar tu pedido.")
                    return redirect('editar_pedido', pedido_id=pedido.id)

                pedido.recalcular_total()
                messages.success(request, f"¡Pedido #{pedido.id} actualizado correctamente!")
                return redirect('mis_pedidos')
        except Exception as e:
            messages.error(request, f"Error al actualizar el pedido: {e}")

    return render(request, 'pedidos/editar_pedido.html', {
        'pedido': pedido,
        'platos': platos_disponibles,
    })


# ==================== VISTAS DE EMPLEADOS / GERENCIA BLINDADAS ====================
@rol_requerido(['ATENCION', 'GERENTE'])
def atencion_dashboard(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    platos = PlatoMenu.objects.filter(activo=True)

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        if nuevo_estado in dict(Pedido.ESTADOS):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f"Pedido #{pedido.id} modificado a {nuevo_estado}.")
            return redirect('atencion_dashboard')

    return render(request, 'pedidos/atencion_dashboard.html', {'pedidos': pedidos, 'platos': platos, 'estados': Pedido.ESTADOS})


@rol_requerido(['REPARTIDOR', 'GERENTE'])
def repartidor_dashboard(request):
    pedidos_ruta = Pedido.objects.all().order_by('-fecha_pedido')
    
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = 'ENTREGADO'
        pedido.repartidor = request.user
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} marcado como ENTREGADO.")
        return redirect('repartidor_dashboard')

    return render(request, 'pedidos/repartidor_dashboard.html', {'pedidos': pedidos_ruta})


@rol_requerido(['GERENTE'])
def gerente_dashboard(request):
    chile_tz = zoneinfo.ZoneInfo('America/Santiago')
    hoy_chile = datetime.now(chile_tz).date()

    menus = PlatoMenu.objects.all().order_by('dia_semana')
    proveedores = Proveedor.objects.all()
    empleados = Usuario.objects.filter(rol__in=['GERENTE', 'ATENCION', 'REPARTIDOR'])
    convenios = EmpresaConvenio.objects.all()
    
    pedidos_todos = Pedido.objects.all().order_by('-fecha_pedido')
    clientes_comunes = Usuario.objects.filter(rol='CLIENTE', empresa_convenio__isnull=True)
    clientes_empresas = Usuario.objects.filter(rol='CLIENTE', empresa_convenio__isnull=False)

    ganancias_dia = sum(
        p.total for p in pedidos_todos 
        if p.pagado and localtime(p.fecha_pedido).date() == hoy_chile
    )

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear_menu':
            PlatoMenu.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion'),
                dia_semana=request.POST.get('dia_semana'),
                precio=request.POST.get('precio'),
                activo=True
            )
            messages.success(request, "Plato incorporado al menú y visible en portada.")

        elif accion == 'crear_proveedor':
            Proveedor.objects.create(
                nombre=request.POST.get('nombre'),
                contacto=request.POST.get('contacto'),
                telefono=request.POST.get('telefono')
            )
            messages.success(request, "Proveedor ingresado.")

        elif accion == 'crear_convenio':
            EmpresaConvenio.objects.create(
                nombre=request.POST.get('nombre'),
                rut=request.POST.get('rut'),
                direccion=request.POST.get('direccion'),
                telefono=request.POST.get('telefono')
            )
            messages.success(request, "Empresa en convenio agregada.")

        elif accion == 'crear_cliente_comun':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            rut = request.POST.get('rut')
            password = request.POST.get('password')

            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "El correo electrónico ya está registrado.")
            else:
                Usuario.objects.create_user(
                    email=email,
                    password=password,
                    nombre=nombre,
                    apellido=apellido,
                    rut=rut,
                    rol='CLIENTE'
                )
                messages.success(request, f"Cliente común {nombre} {apellido} creado con éxito.")

        elif accion == 'crear_cliente_convenio':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            rut = request.POST.get('rut')
            empresa_id = request.POST.get('empresa_convenio')
            password = request.POST.get('password')

            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "El correo electrónico ya está registrado.")
            else:
                empresa = get_object_or_404(EmpresaConvenio, id=empresa_id)
                nuevo_user = Usuario.objects.create_user(
                    email=email,
                    password=password,
                    nombre=nombre,
                    apellido=apellido,
                    rut=rut,
                    rol='CLIENTE',
                    empresa_convenio=empresa
                )
                nuevo_user.saldo_giftcard = 70000
                nuevo_user.save()
                messages.success(request, f"Cliente de convenio {nombre} creado con Gift Card de $70.000.")

        # 🌟 LÓGICA AÑADIDA PARA CREAR CUENTAS DE REPARTIDORES 🌟
        elif accion == 'crear_repartidor':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            rut = request.POST.get('rut')
            password = request.POST.get('password')

            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "El correo electrónico ya está registrado.")
            else:
                Usuario.objects.create_user(
                    email=email,
                    password=password,
                    nombre=nombre,
                    apellido=apellido,
                    rut=rut,
                    rol='REPARTIDOR'
                )
                messages.success(request, f"Cuenta de Repartidor para {nombre} {apellido} creada exitosamente.")

        return redirect('gerente_dashboard')

    return render(request, 'pedidos/gerente_dashboard.html', {
        'menus': menus,
        'proveedores': proveedores,
        'empleados': empleados,
        'convenios': convenios,
        'pedidos_todos': pedidos_todos,
        'clientes_comunes': clientes_comunes,
        'clientes_empresas': clientes_empresas,
        'ganancias_dia': ganancias_dia,
        'dias': PlatoMenu.DIAS
    })


@rol_requerido(['GERENTE'])
def editar_menu_gerente(request, plato_id):
    plato = get_object_or_404(PlatoMenu, id=plato_id)
    if request.method == 'POST':
        plato.nombre = request.POST.get('nombre')
        plato.descripcion = request.POST.get('descripcion')
        plato.dia_semana = request.POST.get('dia_semana')
        plato.precio = request.POST.get('precio')
        plato.save()
        messages.success(request, "Plato actualizado con éxito.")
        return redirect('gerente_dashboard')
    return render(request, 'pedidos/editar_menu.html', {'plato': plato, 'dias': PlatoMenu.DIAS})


@rol_requerido(['GERENTE'])
def eliminar_elemento(request, tipo, item_id):
    if tipo == 'menu':
        get_object_or_404(PlatoMenu, id=item_id).delete()
    elif tipo == 'proveedor':
        get_object_or_404(Proveedor, id=item_id).delete()
    elif tipo == 'empleado':
        get_object_or_404(Usuario, id=item_id).delete()
    elif tipo == 'convenio':
        get_object_or_404(EmpresaConvenio, id=item_id).delete()
    messages.success(request, "Elemento eliminado exitosamente.")
    return redirect('gerente_dashboard')