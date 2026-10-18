from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.constants import DIFFICULTIES
from core.codes import invitation_code


class Classroom(models.Model):
    invite_code = models.CharField(
        "Código de invitación",
        max_length=12,
        unique=True,
        default=invitation_code,
        editable=False,
    )
    name = models.CharField("Nombre del grupo", max_length=100)
    teacher = models.ForeignKey(
        "core.User", on_delete=models.PROTECT, related_name="classrooms"
    )
    active = models.BooleanField("Activo", default=True)

    class Meta:
        db_table = "core_classroom"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField("Nombre o alias", max_length=150, blank=True)
    claim_code = models.CharField(
        "Código personal de vinculación",
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )
    self_registered = models.BooleanField(
        "Registro independiente", default=False, editable=False
    )
    user = models.OneToOneField(
        "core.User",
        on_delete=models.PROTECT,
        related_name="student",
        null=True,
        blank=True,
    )
    teacher = models.ForeignKey(
        "core.User",
        on_delete=models.PROTECT,
        related_name="students",
        null=True,
        blank=True,
    )
    classrooms = models.ManyToManyField(
        "escuela.Classroom",
        db_table="core_student_classrooms",
        blank=True,
        verbose_name="Grupos",
    )
    category = models.ForeignKey(
        "preguntas.Category", on_delete=models.PROTECT, verbose_name="Categoría"
    )
    difficulty = models.PositiveSmallIntegerField(
        "Dificultad", choices=DIFFICULTIES, default=1
    )
    age = models.PositiveSmallIntegerField(
        "Edad", validators=[MinValueValidator(6), MaxValueValidator(99)]
    )
    active = models.BooleanField("Activo", default=True)

    class Meta:
        db_table = "core_student"
        ordering = ["name", "id"]

    def __str__(self):
        return self.name or (
            self.user.first_name or self.user.username if self.user_id else "Explorador"
        )
