"""Dominio acumulado de preguntas únicas y desbloqueos que no se revocan."""

import math
from preguntas.models import Category
from preguntas.models import Question
from progreso.models import Mastery
from progreso.models import WorldUnlock

CODES = ["ALFA", "BETA", "OMEGA"]


def category_for_age(age):
    return Category.objects.get(
        code="ALFA" if age <= 8 else "BETA" if age <= 11 else "OMEGA"
    )


def bank_for(category):
    return Question.objects.filter(
        category=category, status="published", subject__name="Matemáticas"
    )


def worlds(student):
    categories = {c.code: c for c in Category.objects.all()}
    age_rank = 0 if student.age <= 8 else 1 if student.age <= 11 else 2
    assigned_rank = CODES.index(student.category.code)
    unlocked = set(student.world_unlocks.values_list("category__code", flat=True))
    rank = max(age_rank, assigned_rank, max([CODES.index(c) for c in unlocked] + [0]))
    rows = []
    for index, code in enumerate(CODES):
        c = categories[code]
        pool = bank_for(c)
        total = pool.count()
        mastered = Mastery.objects.filter(
            student=student, category=c, question__in=pool
        ).count()
        required = math.ceil(total * 0.8)
        if index <= rank:
            WorldUnlock.objects.get_or_create(student=student, category=c)
            if total and mastered >= required and index < 2:
                rank = max(rank, index + 1)
        rows.append(
            {
                "category": c,
                "unlocked": index <= rank,
                "mastered": mastered,
                "total": total,
                "required": required,
                "percent": min(100, round(mastered / total * 100)) if total else 0,
            }
        )
    return rows


def can_play(student, category):
    return any(
        r["category"].pk == category.pk and r["unlocked"] for r in worlds(student)
    )


def record_mastery(student, item, category):
    Mastery.objects.get_or_create(
        student=student, question=item.question, defaults={"category": category}
    )
    worlds(student)


def learning_tier(student, category):
    tier = 1
    for difficulty in [1, 2]:
        pool = bank_for(category).filter(difficulty=difficulty)
        count = pool.count()
        done = Mastery.objects.filter(
            student=student, question__in=pool, category=category
        ).count()
        if count and done >= math.ceil(count * 0.8):
            tier = difficulty + 1
        else:
            break
    return max(tier, student.difficulty)
