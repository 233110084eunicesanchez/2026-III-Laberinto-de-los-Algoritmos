from django.db import models
from usuarios.models import Usuario
from ejercicios.models import Nivel

# Create your models here.
class Progreso(models.Model):
    id_progreso = models.AutoField(primary_key=True)
    puntaje_total = models.IntegerField()
    fecha_completado = models.DateField(auto_now_add=True)
    fk_alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fk_nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)

    def _str_(self):
        return f"Progreso {self.id_progreso} - {self.fk_alumno.nombre}"