from django.urls import path
from . import views

urlpatterns = [
    path('', views.portada_view, name='portada'),
    path('carrito/', views.carrito_pedido_view, name='carrito_pedido'),
    path('menu/', views.menu_semanal_cliente, name='menu_semanal'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/boleta/<int:pedido_id>/', views.boleta_pedido, name='boleta_pedido'),
    path('pedido/pagar/<int:pedido_id>/', views.pagar_pedido, name='pagar_pedido'),
    path('pedido/eliminar/<int:pedido_id>/', views.eliminar_pedido_cliente, name='eliminar_pedido'),
    path('pedido/editar/<int:pedido_id>/', views.editar_pedido_cliente, name='editar_pedido'),
    path('atencion/', views.atencion_dashboard, name='atencion_dashboard'),
    path('repartidor/', views.repartidor_dashboard, name='repartidor_dashboard'),
    path('gerente/', views.gerente_dashboard, name='gerente_dashboard'),
    path('gerente/menu/editar/<int:plato_id>/', views.editar_menu_gerente, name='editar_menu_gerente'),
    path('gerente/eliminar/<str:tipo>/<int:item_id>/', views.eliminar_elemento, name='eliminar_elemento'),
    path('gerente/editar-usuario/<int:usuario_id>/', views.editar_usuario_gerente, name='editar_usuario_gerente'),
    path('gerente/editar-empresa/<int:empresa_id>/', views.editar_empresa_gerente, name='editar_empresa_gerente'),
]