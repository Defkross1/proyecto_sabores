from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol in roles_permitidos or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Acceso denegado: tu rol no tiene permisos para esta acción.")
        return _wrapped_view
    return decorator
