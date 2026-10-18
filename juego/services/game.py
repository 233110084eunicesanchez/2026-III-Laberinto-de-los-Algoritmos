import random
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from juego.models import Attempt
from juego.models import AttemptQuestion
from progreso.models import Mastery
from escuela.models import Student
from .maze import generate, crash_path
from progreso.services.progress import bank_for, can_play, learning_tier, record_mastery

ACTIVE = ["ready", "board", "quiz"]


def deadline(a, now):
    return now + timedelta(seconds=a.seconds) if a.seconds else None


@transaction.atomic
def create_attempt(student, operator, mode, category=None):
    if mode not in ["mission", "solo", "practice"]:
        raise ValueError("Modalidad no válida.")
    category = category or student.category
    if not can_play(student, category):
        raise ValueError("Ese mundo aún está bloqueado.")
    board = generate(category.code, route_count=1) if mode == "solo" else {}
    total = len(board["routes"][0]) - 1 if mode == "solo" else 5
    tier = learning_tier(student, category)
    pool = list(bank_for(category).filter(difficulty__lte=tier))
    if len(pool) < total:
        pool = list(bank_for(category))
    if len(pool) < total:
        raise ValueError("No hay suficientes preguntas publicadas para esta misión.")
    known = set(
        Mastery.objects.filter(student=student).values_list("question_id", flat=True)
    )
    recent = set(
        AttemptQuestion.objects.filter(attempt__student=student)
        .order_by("-attempt__created_at")
        .values_list("question_id", flat=True)[:20]
    )
    rng = random.SystemRandom()
    rng.shuffle(pool)
    pool.sort(key=lambda q: (q.pk in known, q.pk in recent, q.difficulty))
    chosen = pool[:total]
    a = Attempt.objects.create(
        student=student,
        operator=operator,
        category=category,
        difficulty=tier,
        seconds=0 if category.code == "ALFA" else category.seconds,
        mode=mode,
        board=board,
        total_questions=total,
    )
    for i, q in enumerate(chosen):
        opts = list(enumerate(q.options))
        rng.shuffle(opts)
        snapshot = {
            "text": q.text,
            "options": [v for _, v in opts],
            "correct": next(i for i, (old, _) in enumerate(opts) if old == q.correct),
            "explanation": q.explanation,
            "topic": q.topic,
        }
        AttemptQuestion.objects.create(
            attempt=a, question=q, position=i, snapshot=snapshot
        )
    return a


def sync(a, now=None):
    now = now or timezone.now()
    if a.state != "quiz":
        return
    if a.next_at:  # Compatibilidad con una partida activa de la versión anterior.
        a.next_at = None
        if a.current >= a.total_questions:
            a.state = "won" if a.score >= 3 else "lost"
            a.finished_at = now
            a.deadline = None
        else:
            a.deadline = deadline(a, now)
        a.save()
        return
    if a.deadline and now >= a.deadline:
        record(a, None, now)


def record(a, selected, now=None):
    now = now or timezone.now()
    item = a.items.get(position=a.current)
    if item.answered_at:
        return
    item.selected = selected
    item.correct = selected is not None and selected == item.snapshot["correct"]
    item.answered_at = now
    item.save()
    a.current += 1
    a.score += int(item.correct)
    a.next_at = None
    if item.correct:
        # Serializa el progreso de dos partidas simultáneas del mismo alumno.
        student = Student.objects.select_for_update().get(pk=a.student_id)
        record_mastery(student, item, a.category)
    if a.mode == "solo" and not item.correct:
        a.board["crash_path"] = crash_path(a.board, a.board["routes"][0][a.score])
        a.state = "lost"
    elif a.current >= a.total_questions:
        a.state = "won" if a.mode == "solo" or a.score >= 3 else "lost"
    if a.state in ["won", "lost"]:
        a.finished_at = now
        a.deadline = None
    else:
        a.deadline = deadline(a, now)
    a.save()


@transaction.atomic
def action(attempt_id, command, position=None, selected=None):
    student_id = Attempt.objects.values_list("student_id", flat=True).get(pk=attempt_id)
    Student.objects.select_for_update().get(pk=student_id)
    a = Attempt.objects.select_for_update().get(pk=attempt_id)
    sync(a)
    now = timezone.now()
    if command == "start" and a.state == "ready":
        if a.mode == "mission":
            a.board = generate(a.category.code)
            a.state = "board"
        else:
            a.state = "quiz"
            a.deadline = deadline(a, now)
    elif command == "goal" and a.state == "board":
        a.state = "quiz"
        a.deadline = deadline(a, now)
    elif command == "virus" and a.state == "board":
        a.state = "virus"
        a.finished_at = now
    elif command == "abandon" and a.state in ACTIVE:
        a.state = "abandoned"
        a.finished_at = now
        a.deadline = None
    elif command == "answer" and a.state == "quiz" and position == a.current:
        if type(selected) != int or selected not in range(4):
            raise ValueError("Selecciona una opción válida.")
        record(a, selected, now)
    a.save()
    return a


@transaction.atomic
def status(attempt_id):
    student_id = Attempt.objects.values_list("student_id", flat=True).get(pk=attempt_id)
    Student.objects.select_for_update().get(pk=student_id)
    a = Attempt.objects.select_for_update().get(pk=attempt_id)
    sync(a)
    d = {
        "state": a.state,
        "mode": a.mode,
        "current": a.current,
        "score": a.score,
        "errors": a.current - a.score,
        "total": a.total_questions,
        "seconds": a.seconds,
        "deadline": a.deadline.isoformat() if a.deadline else None,
        "server_now": timezone.now().isoformat(),
        "category": a.category.code,
    }
    if a.state == "board" or (a.mode == "solo" and a.state != "ready"):
        d["board"] = a.board
    if a.current:
        last = a.items.get(position=a.current - 1)
        d["last_answer"] = {
            "position": last.position,
            "correct": last.correct,
            "timeout": last.selected is None,
        }
    if a.state == "quiz":
        item = a.items.get(position=a.current)
        d["question"] = {
            "text": item.snapshot["text"],
            "options": item.snapshot["options"],
            "position": a.current,
        }
    return d


@transaction.atomic
def resume_or_create(student, operator, mode, category):
    """Evita intentos activos duplicados; autorización del objeto se hace en la vista."""
    from django.core.exceptions import PermissionDenied

    student = Student.objects.select_for_update().get(pk=student.pk)
    if not student.active or (student.user_id and not student.user.is_active):
        raise PermissionDenied
    if not can_play(student, category):
        raise PermissionDenied("Mundo aún bloqueado.")
    current = Attempt.objects.filter(
        student=student,
        operator=operator,
        mode=mode,
        category=category,
        state__in=ACTIVE,
    ).first()
    return current or create_attempt(student, operator, mode, category)
