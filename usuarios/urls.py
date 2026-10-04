from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_cliente, name='registro'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('perfil/direccion/<int:direccion_id>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
]