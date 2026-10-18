from django.db.models import Q
from django.shortcuts import get_object_or_404
from core.access import students_for, is_manager


def active_students(user):
    return (
        students_for(user)
        .filter(active=True)
        .filter(Q(user__isnull=True) | Q(user__is_active=True))
    )


def selected_student(request):
    qs = active_students(request.user)
    if is_manager(request.user):
        raw = (
            request.POST.get("student")
            if request.method == "POST"
            else request.GET.get("student")
        )
        if not raw or not str(raw).isdigit():
            return None
        return get_object_or_404(qs, pk=raw)
    return get_object_or_404(qs, user=request.user)


def can_control(user, a):
    return user.is_superuser or (
        a.operator_id == user.pk and (is_manager(user) or a.student.user_id == user.pk)
    )
