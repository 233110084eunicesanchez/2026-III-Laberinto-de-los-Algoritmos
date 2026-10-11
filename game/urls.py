from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_personalizado, name='login_custom'),
    path('logout/', views.logout_personalizado, name='logout_custom'),

    # Administrador
    path('admin-panel/', views.panel_admin_custom, name='panel_admin_custom'),
    path('admin-panel/crear-usuario/', views.crear_usuario_desde_admin, name='admin_crear_usuario'),

    # Maestro
    path('maestro/grupos/', views.lista_grupos_maestro, name='mis_grupos'),
    path('maestro/ejercicio/crear/', views.crear_ejercicio, name='crear_ejercicio'),
    path('maestro/grupo/<int:grupo_id>/', views.detalle_grupo_alumnos, name='detalle_grupo'),

    # Alumno
    path('alumno/niveles/', views.lista_niveles_alumno, name='niveles_alumno'),
    path('alumno/jugar/<int:nivel_id>/', views.jugar_nivel, name='jugar_nivel'),
    path('alumno/perfil/', views.perfil_puntuaciones_alumno, name='perfil_alumno'),
]