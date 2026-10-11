from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    fk_rol = models.ForeignKey(Rol, on_delete=models.RESTRICT)

    def set_password(self, raw_password):
        """Encripta y asigna la contraseña"""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la contraseña ingresada contra el hash guardado"""
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return f"{self.nombre} ({self.fk_rol.nombre_rol})"