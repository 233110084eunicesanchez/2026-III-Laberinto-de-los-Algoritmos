from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from usuarios.models import Usuario, Rol
from .models import Grupo, EjercicioNivel, Puntuacion

# --- LOGIN Y LOGOUT ---
def login_personalizado(request):
    if request.method == 'POST':
        input_user = request.POST.get('username')
        pass_input = request.POST.get('password')
        
        try:
            user = Usuario.objects.get(Q(email=input_user) | Q(nombre=input_user))
            if user.check_password(pass_input):
                request.session['usuario_id'] = user.id_usuario
                request.session['usuario_rol'] = user.fk_rol.nombre_rol
                request.session['usuario_nombre'] = user.nombre

                if user.fk_rol.nombre_rol == 'Admin':
                    return redirect('panel_admin_custom')
                elif user.fk_rol.nombre_rol == 'Teacher':
                    return redirect('mis_grupos')
                else:
                    return redirect('niveles_alumno')
            else:
                return render(request, 'usuarios/login.html', {'error': 'Contraseña incorrecta'})
        except Usuario.DoesNotExist:
            return render(request, 'usuarios/login.html', {'error': 'El usuario no existe'})

    return render(request, 'usuarios/login.html')

def logout_personalizado(request):
    request.session.flush()
    return redirect('login_custom')


# --- PANEL DEL ADMINISTRADOR ---
def panel_admin_custom(request):
    # Desactivado temporalmente para permitir navegación rápida:
    # if request.session.get('usuario_rol') != 'Admin':
    #     raise PermissionDenied("No tienes permisos de Administrador.")

    usuarios = Usuario.objects.all()
    grupos = Grupo.objects.all()
    ejercicios = EjercicioNivel.objects.all()
    
    return render(request, 'game/admin/panel.html', {
        'usuarios': usuarios,
        'grupos': grupos,
        'ejercicios': ejercicios
    })

def crear_usuario_desde_admin(request):
    # if request.session.get('usuario_rol') != 'Admin':
    #     raise PermissionDenied

    roles = Rol.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        id_rol = request.POST.get('rol_id')

        rol_instancia = get_object_or_404(Rol, id_rol=id_rol)
        nuevo_user = Usuario(nombre=nombre, email=email, fk_rol=rol_instancia)
        nuevo_user.set_password(password)
        nuevo_user.save()

        return redirect('panel_admin_custom')

    return render(request, 'game/admin/crear_usuario.html', {'roles': roles})


# --- SECCIONES MAESTRO ---
def lista_grupos_maestro(request):
    # if request.session.get('usuario_rol') not in ['Teacher', 'Admin']:
    #     raise PermissionDenied

    usuario_id = request.session.get('usuario_id')
    if usuario_id and request.session.get('usuario_rol') == 'Teacher':
        grupos = Grupo.objects.filter(maestro_id=usuario_id)
    else:
        grupos = Grupo.objects.all()

    return render(request, 'game/maestro/grupos.html', {'grupos': grupos})

def crear_ejercicio(request):
    # if request.session.get('usuario_rol') not in ['Teacher', 'Admin']:
    #     raise PermissionDenied

    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        usuario_actual = Usuario.objects.filter(id_usuario=usuario_id).first() if usuario_id else Usuario.objects.first()
        
        EjercicioNivel.objects.create(
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion'),
            nivel_dificultad=request.POST.get('dificultad'),
            creado_por=usuario_actual
        )
        return redirect('mis_grupos')

    return render(request, 'game/maestro/crear_ejercicio.html')

def detalle_grupo_alumnos(request, grupo_id=1):
    # if request.session.get('usuario_rol') not in ['Teacher', 'Admin']:
    #     raise PermissionDenied

    grupo = Grupo.objects.filter(id=grupo_id).first()
    alumnos = grupo.alumnos.all() if grupo else []
    return render(request, 'game/maestro/detalle_grupo.html', {'grupo': grupo, 'alumnos': alumnos})


# --- SECCIONES ALUMNO ---
def lista_niveles_alumno(request):
    niveles = EjercicioNivel.objects.all().order_by('nivel_dificultad')
    return render(request, 'game/alumno/niveles.html', {'niveles': niveles})

def jugar_nivel(request, nivel_id=1):
    nivel = EjercicioNivel.objects.filter(id=nivel_id).first()
    return render(request, 'game/alumno/juego.html', {'nivel': nivel})

def perfil_puntuaciones_alumno(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        puntuaciones = Puntuacion.objects.filter(alumno_id=usuario_id)
    else:
        puntuaciones = Puntuacion.objects.all()

    return render(request, 'game/alumno/perfil.html', {'puntuaciones': puntuaciones})