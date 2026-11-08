from django.urls import path
from . import views
from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_votaciones, name='lista_votaciones'),
    path('nueva-edicion/', views.crear_edicion, name='crear_edicion'),
    path('nueva-categoria/<int:edicion_id>/', views.crear_categoria, name='crear_categoria'),
    path('editar-categoria/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('nueva-opcion/<int:votacion_id>/', views.crear_participante, name='crear_participante'),
    path('participante/editar/<int:pk>/', views.editar_participante, name='editar_participante'),
    path('votar/<int:opcion_id>/', views.emitir_voto, name='emitir_voto'),
    
    # Estas son las que faltaban o debían tener exactamente estos nombres:
    path('login/', views.login_votante, name='login_votante'),
    path('registro/', views.registro_votante, name='registro_votante'),
    path('salir/', views.cerrar_sesion_votante, name='logout_votante'),
    path('salir/', views.cerrar_sesion_votante, name='cerrar_sesion'),
    path('resultados/', views.ver_resultados_admin, name='resultados_admin'),

    path('api/ediciones/', views.api_lista_ediciones, name='api_lista_ediciones'),
    path('edicion/desactivar/<int:pk>/', views.desactivar_edicion, name='desactivar_edicion'),
    path('edicion/activar/<int:pk>/', views.activar_edicion, name='activar_edicion'),
    path('categoria/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('participante/eliminar/<int:pk>/', views.eliminar_participante, name='eliminar_participante'),
    path('edicion/eliminar/<int:pk>/', views.eliminar_edicion, name='eliminar_edicion'),
    
]