"""
URLs de la app core.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_docente, name='registro_docente'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Actividades
    path('actividades/', views.actividades_lista, name='actividades_lista'),
    path('actividades/nueva/', views.actividad_crear, name='actividad_crear'),
    path('actividades/<int:pk>/', views.actividad_detalle, name='actividad_detalle'),
    path('actividades/<int:pk>/editar/', views.actividad_editar, name='actividad_editar'),
    path('actividades/<int:pk>/eliminar/', views.actividad_eliminar, name='actividad_eliminar'),
    path('actividades/<int:pk>/evidencia/', views.evidencia_subir_actividad, name='evidencia_subir_actividad'),
    path('actividades/<int:pk>/pdf/', views.reporte_actividad_pdf, name='reporte_actividad_pdf'),

    # Propuestas
    path('propuestas/', views.propuestas_lista, name='propuestas_lista'),
    path('propuestas/nueva/', views.propuesta_crear, name='propuesta_crear'),
    path('propuestas/<int:pk>/', views.propuesta_detalle, name='propuesta_detalle'),
    path('propuestas/<int:pk>/revisar/', views.propuesta_revisar, name='propuesta_revisar'),
    path('propuestas/<int:pk>/eliminar/', views.propuesta_eliminar, name='propuesta_eliminar'),

    # Excursiones
    path('excursiones/', views.excursiones_lista, name='excursiones_lista'),
    path('excursiones/nueva/', views.excursion_crear, name='excursion_crear'),
    path('excursiones/<int:pk>/', views.excursion_detalle, name='excursion_detalle'),
    path('excursiones/<int:pk>/editar/', views.excursion_editar, name='excursion_editar'),
    path('excursiones/<int:pk>/eliminar/', views.excursion_eliminar, name='excursion_eliminar'),
    path('excursiones/<int:pk>/evidencia/', views.evidencia_subir_excursion, name='evidencia_subir_excursion'),

    # Evidencias
    path('evidencias/<int:pk>/eliminar/', views.evidencia_eliminar, name='evidencia_eliminar'),

    # Avisos
    path('avisos/', views.avisos_lista, name='avisos_lista'),
    path('avisos/nuevo/', views.aviso_crear, name='aviso_crear'),
    path('avisos/<int:pk>/eliminar/', views.aviso_eliminar, name='aviso_eliminar'),

    # Mensajería
    path('mensajes/', views.mensajes_bandeja, name='mensajes_bandeja'),
    path('mensajes/nuevo/', views.mensaje_enviar, name='mensaje_enviar'),
    path('mensajes/<int:pk>/', views.mensaje_leer, name='mensaje_leer'),

    # Calendario
    path('calendario/', views.calendario_actividades, name='calendario_actividades'),

    # Reportes
    path('reportes/', views.reportes_panel, name='reportes_panel'),
    path('reportes/pdf/', views.reporte_general_pdf, name='reporte_general_pdf'),

    # Perfil
    path('perfil/', views.perfil, name='perfil'),

    # Configuración de Usuarios (Director)
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuarios/nuevo/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='usuario_eliminar'),

    # Config
    path('config/secciones/', views.secciones_lista, name='secciones_lista'),
    path('config/destinos/', views.destinos_lista, name='destinos_lista'),

]
