import uuid
from django.db import models
from core.constants import DIFFICULTIES


class Attempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "escuela.Student", on_delete=models.PROTECT, related_name="attempts"
    )
    operator = models.ForeignKey("core.User", on_delete=models.PROTECT)
    category = models.ForeignKey("preguntas.Category", on_delete=models.PROTECT)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTIES)
    seconds = models.PositiveSmallIntegerField()
    mode = models.CharField(
        max_length=10,
        choices=[
            ("mission", "Dinámico"),
            ("solo", "Individual"),
            ("practice", "Práctica anterior"),
        ],
    )
    state = models.CharField(
        max_length=12,
        default="ready",
        choices=[
            ("ready", "Preparación"),
            ("board", "Recorrido"),
            ("quiz", "Preguntas"),
            ("won", "Victoria"),
            ("lost", "Reto no superado"),
            ("virus", "Virus"),
            ("abandoned", "Interrumpida"),
        ],
    )
    board = models.JSONField(default=dict)
    total_questions = models.PositiveSmallIntegerField(default=5)
    current = models.PositiveSmallIntegerField(default=0)
    deadline = models.DateTimeField(null=True, blank=True)
    next_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    display_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_attempt"
        ordering = ["-created_at"]
        permissions = [("conduct_attempt", "Puede dirigir misiones")]


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(
        "juego.Attempt", on_delete=models.CASCADE, related_name="items"
    )
    question = models.ForeignKey("preguntas.Question", on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    snapshot = models.JSONField()
    selected = models.SmallIntegerField(null=True, blank=True)
    correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_attemptquestion"
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "position"], name="one_question_per_position"
            )
        ]
