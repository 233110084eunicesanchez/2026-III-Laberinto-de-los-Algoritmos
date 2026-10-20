"""Registro público y vinculación voluntaria, separados de las vistas HTML."""

from django.core.exceptions import ValidationError
from django.db import transaction
from escuela.models import Student
from escuela.models import Classroom


def resolve_invitation(code):
    return Classroom.objects.filter(
        invite_code=code.strip().upper(), active=True, teacher__is_active=True
    ).first()


@transaction.atomic
def join_group(student_id, code):
    student = Student.objects.select_for_update().get(pk=student_id)
    room = (
        Classroom.objects.select_for_update()
        .filter(invite_code=code.strip().upper(), active=True, teacher__is_active=True)
        .first()
    )
    if not room:
        raise ValidationError(
            "Ese código no está disponible. Revísalo con tu profesor."
        )
    if not room.teacher.has_perm("juego.conduct_attempt"):
        raise ValidationError("Ese grupo no admite inscripciones en este momento.")
    if student.teacher_id and student.teacher_id != room.teacher_id:
        raise ValidationError(
            "Ya tienes otro profesor responsable. Pide al administrador que revise el cambio."
        )
    if not student.active or (student.user_id and not student.user.is_active):
        raise ValidationError("Tu cuenta no está activa.")
    student.teacher = room.teacher
    student.save(update_fields=["teacher"])
    student.classrooms.add(room)
    return room


@transaction.atomic
def claim_profile(user, code):
    from juego.models import Attempt
    from progreso.models import Mastery
    from progreso.models import WorldUnlock

    # Orden consistente para evitar bloqueos cruzados entre reclamaciones.
    current = Student.objects.get(user=user)
    target = Student.objects.filter(
        claim_code=code.strip().lower(), user__isnull=True, active=True
    ).first()
    if not target:
        raise ValidationError(
            "Código personal no disponible. Pide a tu profesor que lo revise."
        )
    locked = {
        s.pk: s
        for s in Student.objects.select_for_update()
        .filter(pk__in=[current.pk, target.pk])
        .order_by("pk")
    }
    current, target = locked[current.pk], locked[target.pk]
    if target.user_id or target.claim_code != code.strip().lower():
        raise ValidationError("Este código ya fue utilizado.")
    if current.teacher_id and current.teacher_id != target.teacher_id:
        raise ValidationError(
            "Tu cuenta tiene otro profesor responsable. Consulta al administrador."
        )
    if not current.active or not user.is_active:
        raise ValidationError("Tu cuenta no está activa.")
    if (
        not target.teacher_id
        or not target.teacher.is_active
        or not target.teacher.has_perm("juego.conduct_attempt")
    ):
        raise ValidationError("El profesor no está disponible.")
    for m in current.masteries.all():
        Mastery.objects.get_or_create(
            student=target, question=m.question, defaults={"category": m.category}
        )
    for u in current.world_unlocks.all():
        WorldUnlock.objects.get_or_create(student=target, category=u.category)
    Attempt.objects.filter(student=current).update(student=target)
    target.classrooms.add(*current.classrooms.all())
    current.user = None
    current.save(update_fields=["user"])
    target.user = user
    target.self_registered = True
    target.claim_code = None
    target.save()
    current.delete()
    from progreso.services.progress import worlds

    worlds(target)
    return target
