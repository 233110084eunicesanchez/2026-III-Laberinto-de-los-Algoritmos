from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from preguntas.models import Question
from preguntas.forms import QuestionForm
from core.access import questions_for

from django.views import View
from core.mixins import SchoolPermission, ScopedQuerysetMixin


class QuestionList(SchoolPermission, ListView):
    permission_required = "preguntas.view_question"
    template_name = "preguntas/questions.html"
    paginate_by = 20

    def get_queryset(self):
        qs = questions_for(self.request.user)
        term = self.request.GET.get("q", "")
        return qs.filter(text__icontains=term)


class QuestionDetail(ScopedQuerysetMixin, SchoolPermission, DetailView):
    permission_required = "preguntas.view_question"
    template_name = "preguntas/question_detail.html"
    scope = staticmethod(questions_for)


class QuestionCreate(SchoolPermission, CreateView):
    permission_required = "preguntas.add_question"
    model = Question
    form_class = QuestionForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("preguntas:questions")
    extra_context = {
        "title": "Proponer pregunta",
        "hint": "Se guardará como borrador para revisión del administrador.",
    }

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class QuestionUpdate(ScopedQuerysetMixin, SchoolPermission, UpdateView):
    permission_required = "preguntas.change_question"
    form_class = QuestionForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("preguntas:questions")
    extra_context = {
        "title": "Editar pregunta",
        "hint": "Al editar, vuelve a borrador. Las partidas anteriores conservan su versión.",
    }
    scope = staticmethod(questions_for)

    def form_valid(self, form):
        form.instance.status = "draft"
        return super().form_valid(form)


class QuestionDelete(ScopedQuerysetMixin, SchoolPermission, DeleteView):
    permission_required = "preguntas.delete_question"
    template_name = "shared/delete.html"
    success_url = reverse_lazy("preguntas:questions")
    scope = staticmethod(questions_for)

    def form_valid(self, form):
        if self.object.attemptquestion_set.exists():
            self.object.status = "retired"
            self.object.save()
            messages.info(self.request, "Pregunta retirada; historial conservado.")
            return redirect(self.success_url)
        return super().form_valid(form)


class PublishView(SchoolPermission, View):
    permission_required = "preguntas.publish_question"

    def post(self, request, pk):
        q = get_object_or_404(questions_for(request.user), pk=pk)
        q.full_clean()
        q.status = "published"
        q.save()
        return redirect("preguntas:questions")
