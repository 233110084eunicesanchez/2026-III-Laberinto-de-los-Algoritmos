from .models import Student, Classroom, Question, Attempt


def is_manager(user):
    return user.is_authenticated and user.has_perm("juego.conduct_attempt")


def students_for(user):
    qs = Student.objects.select_related("user", "category", "teacher")
    if user.is_superuser:
        return qs
    if not user.has_perm("escuela.view_student"):
        return qs.none()
    if is_manager(user):
        return qs.filter(teacher=user)
    return qs.filter(user=user) if user.has_perm("escuela.view_student") else qs.none()


def classrooms_for(user):
    qs = Classroom.objects.all()
    return qs if user.is_superuser else qs.filter(teacher=user)


def questions_for(user):
    qs = Question.objects.select_related("category", "subject")
    return qs if user.is_superuser else qs.filter(author=user)


def attempts_for(user):
    qs = Attempt.objects.select_related("student__user", "category")
    if user.is_superuser:
        return qs
    if not user.has_perm("juego.view_attempt"):
        return qs.none()
    if is_manager(user):
        return qs.filter(student__teacher=user)
    return (
        qs.filter(student__user=user)
        if user.has_perm("juego.view_attempt")
        else qs.none()
    )
