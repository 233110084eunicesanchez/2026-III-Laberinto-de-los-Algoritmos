"""Acceso común: autenticación, permiso de acción y alcance por objeto."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.access import attempts_for
from juego.models import Attempt
from juego.selectors import can_control


class SchoolPermission(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


class AttemptAccessMixin(LoginRequiredMixin):
    control_required = False

    def get_attempt(self):
        attempt = get_object_or_404(
            attempts_for(self.request.user), pk=self.kwargs["pk"]
        )
        if self.control_required and not can_control(self.request.user, attempt):
            raise PermissionDenied
        return attempt


class DisplayAccessMixin:
    """Capacidad pública explícita: token aleatorio, ocho horas, solo lectura."""

    def get_attempt(self):
        return get_object_or_404(
            Attempt,
            display_token=self.kwargs["token"],
            created_at__gte=timezone.now() - timezone.timedelta(hours=8),
        )


class OperatorFormMixin:
    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "operator": self.request.user}


class ScopedQuerysetMixin:
    """La vista elige una función de alcance; Detail/Update/Delete la reutilizan."""

    scope = None

    def get_queryset(self):
        return self.scope(self.request.user)
