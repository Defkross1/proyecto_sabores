from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.tipo_registro_view, name='tipo_registro'),
    path('registro/cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro/empresa/', views.registro_empresa_convenio, name='registro_empresa'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('perfil/direccion/<int:direccion_id>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
]