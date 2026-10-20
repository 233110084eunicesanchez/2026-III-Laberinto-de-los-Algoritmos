from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction
from core.models import User
from escuela.models import Student
from preguntas.models import Category


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Tu nombre o alias", max_length=150)
    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        help_text="Obligatorio para profesores. Para alumnos es opcional: puedes usar un correo de recuperación de tu tutor.",
    )
    role = forms.ChoiceField(
        label="Quiero entrar como",
        choices=[("student", "Alumno"), ("teacher", "Profesor")],
        widget=forms.RadioSelect,
    )
    age = forms.IntegerField(
        label="Edad del alumno",
        min_value=6,
        max_value=14,
        required=False,
        help_text="Asignaremos Alfa (6–8), Beta (9–11) u Omega (12–14).",
    )
    group_code = forms.CharField(
        label="Código de grupo (opcional)",
        max_length=12,
        required=False,
        help_text="Puedes empezar sin grupo. Si introduces un código, el profesor podrá ver tu progreso y ajustar tu nivel.",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "username",
            "email",
            "role",
            "age",
            "group_code",
            "password1",
            "password2",
        ]

    def clean_username(self):
        username = super().clean_username()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "Ese nombre de usuario ya está en uso. Elige otro."
            )
        return username

    def clean(self):
        data = super().clean()
        role = data.get("role")
        if role == "teacher" and not data.get("email"):
            self.add_error(
                "email", "Indica un correo electrónico para tu cuenta de profesor."
            )
        required_group = {"student": "Alumno", "teacher": "Profesor"}.get(role)
        if required_group and not Group.objects.filter(name=required_group).exists():
            raise forms.ValidationError(
                "El registro estará disponible cuando se complete la configuración inicial."
            )
        if role == "student":
            age = data.get("age")
            if age is None:
                self.add_error("age", "Indica tu edad para preparar tu categoría.")
            else:
                code = "ALFA" if age <= 8 else "BETA" if age <= 11 else "OMEGA"
                self.category = Category.objects.filter(code=code).first()
                if not self.category:
                    raise forms.ValidationError(
                        "Falta configurar esta categoría. Contacta al administrador."
                    )
            code = data.get("group_code", "").strip().upper()
            if code:
                from escuela.services.accounts import resolve_invitation

                room = resolve_invitation(code)
                if not room or not room.teacher.has_perm("juego.conduct_attempt"):
                    self.add_error(
                        "group_code",
                        "Ese código no está disponible. Revísalo o continúa sin grupo.",
                    )
            data["group_code"] = code
        return data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save()
        role = self.cleaned_data["role"]
        user.groups.add(
            Group.objects.get(name="Profesor" if role == "teacher" else "Alumno")
        )
        if role == "student":
            student = Student.objects.create(
                user=user,
                name=user.first_name,
                teacher=None,
                age=self.cleaned_data["age"],
                category=self.category,
                difficulty=1,
                self_registered=True,
            )
            if self.cleaned_data.get("group_code"):
                from escuela.services.accounts import join_group

                join_group(student.pk, self.cleaned_data["group_code"])
        return user


class ProfileForm(forms.Form):
    email = forms.EmailField(label="Correo de recuperación", required=False)
    age = forms.IntegerField(
        label="Mi edad actual",
        min_value=6,
        max_value=99,
        required=False,
        help_text="Actualiza tu edad cuando cumplas años. Los mundos ya ganados no se bloquean.",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["email"].initial = user.email
        if not hasattr(user, "student"):
            self.fields.pop("age")
            self.fields["email"].required = not user.is_superuser
        else:
            self.fields["age"].initial = user.student.age
            self.fields["age"].required = True

    @transaction.atomic
    def save(self):
        self.user.email = self.cleaned_data["email"]
        self.user.save(update_fields=["email"])
        if hasattr(self.user, "student"):
            student = self.user.student
            student.age = self.cleaned_data["age"]
            student.save(update_fields=["age"])
            from progreso.services.progress import worlds

            worlds(student)
