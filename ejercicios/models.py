from django.db import models
from usuarios.models import Usuario

# Create your models here.
class Nivel(models.Model):
    id_nivel = models.AutoField(primary_key=True)
    nombre_nivel = models.CharField(max_length=50)
    descripcion = models.TextField()

    def _str_(self):
        return self.nombre_nivel

class Ejercicio(models.Model):
    id_ejercicio = models.AutoField(primary_key=True)
    pregunta = models.CharField(max_length=255)
    op_correcta = models.CharField(max_length=100)
    op_falsa1 = models.CharField(max_length=100)
    op_falsa2 = models.CharField(max_length=100)
    fk_nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    fk_docente = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def _str_(self):
        return self.pregunta