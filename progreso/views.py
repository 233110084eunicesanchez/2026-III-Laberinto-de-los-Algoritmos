from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView
from core.access import attempts_for
from juego.services import game
from juego.themes import theme_for, outcome

from django.views import View
from core.mixins import AttemptAccessMixin
from juego.selectors import can_control


class History(LoginRequiredMixin, ListView):
    template_name = "progreso/history.html"
    paginate_by = 25

    def get_queryset(self):
        qs = attempts_for(self.request.user)
        mode = self.request.GET.get("mode")
        return qs.filter(mode=mode) if mode in ["mission", "practice", "solo"] else qs


class ResultView(AttemptAccessMixin, View):
    def get(self, request, pk):
        a = self.get_attempt()
        if a.state in game.ACTIVE:
            return redirect("juego:play", pk=a.pk)
        return render(
            request,
            "progreso/result.html",
            {
                "attempt": a,
                "items": a.items.filter(answered_at__isnull=False),
                "controller": can_control(request.user, a),
                "theme": theme_for(a.category.code),
                "result_title": outcome(a)[0],
                "result_detail": outcome(a)[1],
                "game_theme": True,
            },
        )
