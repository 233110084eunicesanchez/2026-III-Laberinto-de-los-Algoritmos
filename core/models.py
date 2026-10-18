"""Identidad estable y exportaciones para migraciones/importaciones anteriores.
Los modelos de dominio se definen una sola vez en su propia app.
"""
from django.contrib.auth.models import AbstractUser
from .constants import DIFFICULTIES
from .codes import invitation_code

class User(AbstractUser):
    """Usuario histórico: conservar AUTH_USER_MODEL evita reconstruir cuentas."""
    pass

from preguntas.models import Subject, Category, Question
from escuela.models import Classroom, Student
from juego.models import Attempt, AttemptQuestion
from progreso.models import Mastery, WorldUnlock
