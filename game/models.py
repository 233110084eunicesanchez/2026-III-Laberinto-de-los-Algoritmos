from django.db import models
from usuarios.models import Usuario  # Tu modelo personalizado

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_acceso = models.CharField(max_length=20, unique=True)
    maestro = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='grupos_creados'
    )
    alumnos = models.ManyToManyField(
        Usuario, 
        related_name='grupos_inscritos', 
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} - {self.maestro.nombre}"


class EjercicioNivel(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    nivel_dificultad = models.IntegerField(default=1)
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='ejercicios_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nivel {self.nivel_dificultad}: {self.titulo}"


class Puntuacion(models.Model):
    alumno = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='puntuaciones'
    )
    ejercicio = models.ForeignKey(EjercicioNivel, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)
    tiempo_segundos = models.IntegerField(default=0)
    completado = models.BooleanField(default=False)
    fecha_juego = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('alumno', 'ejercicio')