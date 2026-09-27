from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario

def login_view(request):
    if request.method == 'POST':
        email_post = request.POST.get('email')
        password_post = request.POST.get('password')

        try:
            # Busca si el correo existe en la base de datos
            usuario = Usuario.objects.get(email=email_post)
            
            # Valida la contraseña (Nota: en el futuro se debe usar un hash real)
            if usuario.password_hash == password_post:
                # Crear la sesión para mantener al usuario conectado
                request.session['usuario_id'] = usuario.id_usuario
                request.session['rol_id'] = usuario.fk_rol.id_rol
                request.session['nombre_usuario'] = usuario.nombre
                
                # Redirige dependiendo del rol (1=Docente, 2=Alumno por ejemplo)
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta.')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no está registrado.')

    return render(request, 'usuarios/login.html')