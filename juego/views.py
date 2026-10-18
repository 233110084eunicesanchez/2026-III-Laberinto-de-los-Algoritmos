import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from preguntas.models import Category
from core.access import is_manager
from juego.services import game
from juego.themes import theme_for
from progreso.services.progress import can_play

from django.views import View
from core.mixins import AttemptAccessMixin, DisplayAccessMixin
from juego.selectors import selected_student, can_control


class ChooseModeView(LoginRequiredMixin, View):
    def get(self, request, code):
        student = selected_student(request)
        if not student:
            return redirect("inicio:home")
        category = get_object_or_404(Category, code=code)
        if not can_play(student, category):
            return HttpResponseForbidden("Mundo aún bloqueado.")
        return render(
            request,
            "juego/modes.html",
            {
                "student": student,
                "category": category,
                "theme": theme_for(category.code),
                "game_theme": True,
            },
        )


class StartView(LoginRequiredMixin, View):
    def post(self, request):
        student = selected_student(request)
        if not student:
            return redirect("inicio:home")
        category = get_object_or_404(
            Category, code=request.POST.get("category", student.category.code)
        )
        mode = request.POST.get(
            "mode", "mission" if is_manager(request.user) else "solo"
        )
        if mode not in ["solo", "mission"]:
            return HttpResponseBadRequest("Modalidad no válida.")
        try:
            a = game.resume_or_create(student, request.user, mode, category)
        except ValueError as error:
            messages.error(request, str(error))
            return redirect("inicio:home")
        return redirect("juego:play", pk=a.pk)


class PlayView(AttemptAccessMixin, View):
    def get(self, request, pk):
        a = self.get_attempt()
        return render(
            request,
            "juego/play.html",
            {
                "attempt": a,
                "controller": can_control(request.user, a),
                "theme": theme_for(a.category.code),
                "game_theme": True,
            },
        )


class ApiStatusView(AttemptAccessMixin, View):
    def get(self, request, pk):
        a = self.get_attempt()
        response = JsonResponse(game.status(a.pk))
        response["Cache-Control"] = "no-store"
        return response


class ApiActionView(AttemptAccessMixin, View):
    control_required = True

    def post(self, request, pk):
        a = self.get_attempt()
        try:
            body = json.loads(request.body)
            if not isinstance(body, dict):
                raise ValueError("Se esperaba un objeto JSON.")
            command = body.get("command")
            if command not in ["start", "goal", "virus", "answer", "abandon"]:
                raise ValueError("Acción no válida.")
            position = body.get("position")
            selected = body.get("selected")
            if command == "answer" and (type(position) != int or type(selected) != int):
                raise ValueError("Respuesta no válida.")
            game.action(a.pk, command, position, selected)
            return JsonResponse(game.status(a.pk))
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({"error": str(e)}, status=400)


class RetryView(AttemptAccessMixin, View):
    control_required = True

    def post(self, request, pk):
        a = self.get_attempt()
        if a.state in game.ACTIVE:
            return redirect("juego:play", pk=a.pk)
        if not a.student.active or (a.student.user_id and not a.student.user.is_active):
            return HttpResponseForbidden()
        try:
            new = game.resume_or_create(a.student, request.user, a.mode, a.category)
        except ValueError as error:
            messages.error(request, str(error))
            return redirect("inicio:home")
        return redirect("juego:play", pk=new.pk)


class DisplayView(DisplayAccessMixin, View):
    def get(self, request, token):
        a = self.get_attempt()
        return render(
            request,
            "juego/display.html",
            {"attempt": a, "theme": theme_for(a.category.code)},
        )


class DisplayStatusView(DisplayAccessMixin, View):
    def get(self, request, token):
        a = self.get_attempt()
        d = game.status(a.pk)
        if "board" in d and d["mode"] == "mission":
            d["board"] = {k: v for k, v in d["board"].items() if k != "routes"}
        r = JsonResponse(d)
        r["Cache-Control"] = "no-store"
        return r
