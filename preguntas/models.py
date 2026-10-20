from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from core.constants import DIFFICULTIES


class Subject(models.Model):
    name = models.CharField("Nombre", max_length=80, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "core_subject"


class Category(models.Model):
    code = models.CharField(
        "Código",
        max_length=8,
        unique=True,
        choices=[("ALFA", "Alfa"), ("BETA", "Beta"), ("OMEGA", "Omega")],
    )
    name = models.CharField("Mundo", max_length=80)
    min_age = models.PositiveSmallIntegerField("Edad mínima")
    max_age = models.PositiveSmallIntegerField("Edad máxima")
    seconds = models.PositiveSmallIntegerField(
        "Segundos", validators=[MinValueValidator(0), MaxValueValidator(40)]
    )
    routes = models.PositiveSmallIntegerField("Rutas", choices=[(1, "Una"), (2, "Dos")])

    class Meta:
        db_table = "core_category"
        ordering = ["min_age"]

    def __str__(self):
        return self.code

    def clean(self):
        if self.code == "ALFA" and self.seconds != 0:
            raise ValidationError({"seconds": "Alfa no tiene límite: usa 0."})
        if self.code != "ALFA" and not 1 <= self.seconds <= 40:
            raise ValidationError(
                {"seconds": "Beta y Omega requieren entre 1 y 40 segundos."}
            )
        expected = 1 if self.code == "OMEGA" else 2
        if self.routes != expected:
            raise ValidationError(
                {"routes": "Alfa y Beta tienen dos rutas; Omega tiene una."}
            )


class Question(models.Model):
    subject = models.ForeignKey(
        "preguntas.Subject", on_delete=models.PROTECT, verbose_name="Materia"
    )
    category = models.ForeignKey(
        "preguntas.Category", on_delete=models.PROTECT, verbose_name="Categoría"
    )
    difficulty = models.PositiveSmallIntegerField("Dificultad", choices=DIFFICULTIES)
    topic = models.CharField("Tema", max_length=80)
    text = models.CharField("Pregunta", max_length=350)
    option_a = models.CharField("Opción A", max_length=100)
    option_b = models.CharField("Opción B", max_length=100)
    option_c = models.CharField("Opción C", max_length=100)
    option_d = models.CharField("Opción D", max_length=100)
    correct = models.PositiveSmallIntegerField(
        "Opción correcta", choices=[(0, "A"), (1, "B"), (2, "C"), (3, "D")]
    )
    explanation = models.CharField("Explicación", max_length=500)
    status = models.CharField(
        "Estado",
        max_length=12,
        choices=[
            ("draft", "Borrador"),
            ("published", "Publicada"),
            ("retired", "Retirada"),
        ],
        default="draft",
    )
    author = models.ForeignKey(
        "core.User", on_delete=models.PROTECT, null=True, blank=True
    )
    seed_key = models.CharField(
        max_length=50, unique=True, null=True, blank=True, editable=False
    )

    class Meta:
        db_table = "core_question"
        permissions = [("publish_question", "Puede publicar preguntas")]
        ordering = ["category", "difficulty", "id"]

    def __str__(self):
        return self.text

    def clean(self):
        opts = [x.strip().casefold() for x in self.options]
        if len(set(opts)) != 4:
            raise ValidationError("Las cuatro opciones deben ser diferentes.")

    @property
    def options(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]
