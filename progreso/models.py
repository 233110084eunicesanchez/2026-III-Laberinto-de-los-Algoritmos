from django.db import models


class Mastery(models.Model):
    student = models.ForeignKey(
        "escuela.Student", on_delete=models.CASCADE, related_name="masteries"
    )
    question = models.ForeignKey("preguntas.Question", on_delete=models.PROTECT)
    category = models.ForeignKey("preguntas.Category", on_delete=models.PROTECT)
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_mastery"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "question"], name="one_mastery_per_question"
            )
        ]


class WorldUnlock(models.Model):
    student = models.ForeignKey(
        "escuela.Student", on_delete=models.CASCADE, related_name="world_unlocks"
    )
    category = models.ForeignKey("preguntas.Category", on_delete=models.PROTECT)
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_worldunlock"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "category"], name="one_unlock_per_world"
            )
        ]
