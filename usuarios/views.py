from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import RegistroClienteForm, LoginForm, DireccionForm, RegistroEmpresaConvenioForm
from .models import DireccionCliente
from .validators import ReglaContrasenaSaboresValidator, NoContieneNombreValidator

def login_view(request):
    if request.user.is_authenticated:
        return redirigir_segun_rol(request.user)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return redirigir_segun_rol(user)
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def tipo_registro_view(request):
    if request.user.is_authenticated:
        return redirigir_segun_rol(request.user)
    return render(request, 'usuarios/tipo_registro.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Cuenta creada exitosamente!")
            return redirect('menu_semanal')
    else:
        form = RegistroClienteForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def registro_empresa_convenio(request):
    if request.method == 'POST':
        form = RegistroEmpresaConvenioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Cuenta de empresa en convenio creada con éxito!")
            return redirect('menu_semanal')
    else:
        form = RegistroEmpresaConvenioForm()
    return render(request, 'usuarios/registro_empresa.html', {'form': form})

def redirigir_segun_rol(user):
    if user.rol == 'GERENTE':
        return redirect('gerente_dashboard')
    elif user.rol == 'ATENCION':
        return redirect('atencion_dashboard')
    elif user.rol == 'REPARTIDOR':
        return redirect('repartidor_dashboard')
    return redirect('menu_semanal')

@login_required
def perfil_cliente(request):
    usuario = request.user
    form_direccion = DireccionForm()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # 1. Actualizar teléfono
        if accion == 'actualizar_telefono':
            nuevo_tel = request.POST.get('telefono')
            if nuevo_tel:
                usuario.telefono = nuevo_tel
                usuario.save()
                messages.success(request, "Teléfono actualizado con éxito.")

        # 2. Agregar nueva dirección
        elif accion == 'nueva_direccion':
            form_direccion = DireccionForm(request.POST)
            if form_direccion.is_valid():
                nueva_dir = form_direccion.save(commit=False)
                nueva_dir.cliente = usuario
                nueva_dir.save()
                messages.success(request, "Dirección agregada correctamente.")
                return redirect('perfil_cliente')

        # 3. Cambiar clave con validaciones de seguridad
        elif accion == 'cambiar_clave':
            nueva_clave = request.POST.get('nueva_clave')
            try:
                ReglaContrasenaSaboresValidator().validate(nueva_clave)
                NoContieneNombreValidator().validate(nueva_clave, user=usuario)
                usuario.set_password(nueva_clave)
                usuario.save()
                update_session_auth_hash(request, usuario)
                messages.success(request, "Contraseña actualizada exitosamente.")
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)

    direcciones = usuario.direcciones.all()
    return render(request, 'usuarios/perfil.html', {
        'direcciones': direcciones,
        'form_direccion': form_direccion,
        'puede_eliminar_direccion': direcciones.count() > 1
    })

@login_required
def eliminar_direccion(request, direccion_id):
    direccion = get_object_or_404(DireccionCliente, id=direccion_id, cliente=request.user)
    try:
        direccion.delete()
        messages.success(request, "Dirección eliminada.")
    except ValidationError as e:
        messages.error(request, str(e.message))
    return redirect('perfil_cliente')