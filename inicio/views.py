from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from preguntas.models import Category
from core.access import is_manager, classrooms_for, attempts_for
from juego.services import game
from juego.themes import theme_for
from progreso.services.progress import worlds

from django.views import View
from juego.selectors import active_students


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        manager = is_manager(request.user)
        students = active_students(request.user)
        group = request.GET.get("group", "")
        if manager and group.isdigit():
            students = students.filter(
                classrooms__in=classrooms_for(request.user).filter(pk=group)
            )
        chosen = request.GET.get("student", "")
        student = (
            students.filter(pk=chosen).first() if chosen.isdigit() else students.first()
        )
        if not manager:
            student = students.filter(user=request.user).first()
        qs = attempts_for(request.user)
        rows = (
            worlds(student)
            if student
            else [
                {
                    "category": c,
                    "unlocked": False,
                    "mastered": 0,
                    "total": 0,
                    "percent": 0,
                    "required": 0,
                }
                for c in Category.objects.all()
            ]
        )
        for row in rows:
            row["theme"] = theme_for(row["category"].code)
        return render(
            request,
            "inicio/home.html",
            {
                "worlds": rows,
                "student": student,
                "students": students,
                "classrooms": classrooms_for(request.user) if manager else [],
                "selected_group": group,
                "recent": qs[:6],
                "played": qs.exclude(state__in=game.ACTIVE).count(),
                "won": qs.filter(state="won").count(),
                "game_theme": True,
            },
        )
