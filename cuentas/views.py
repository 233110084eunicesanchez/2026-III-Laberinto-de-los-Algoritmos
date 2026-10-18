from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from cuentas.forms import RegistrationForm, ProfileForm
from escuela.models import Student
from progreso.services.progress import worlds


class RegisterView(FormView):
    template_name = "cuentas/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("inicio:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            user = form.save()
        except IntegrityError:
            form.add_error(
                None, "No se pudo crear la cuenta. Prueba otro nombre de usuario."
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            login(self.request, user)
            messages.success(self.request, "¡Tu cuenta está lista! Ya puedes comenzar.")
            return super().form_valid(form)
        return self.form_invalid(form)


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "cuentas/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("cuentas:profile")

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "user": self.request.user}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.filter(user=self.request.user).first()
        context.update(student=student, worlds=worlds(student) if student else [])
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Perfil actualizado.")
        return super().form_valid(form)
