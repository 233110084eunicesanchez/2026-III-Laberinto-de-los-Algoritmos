from django import forms
from django.db import transaction
from escuela.models import Student
from escuela.models import Classroom
from core.access import classrooms_for


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ["name", "active"]


class GroupChoiceForm(forms.Form):
    classroom = forms.ModelChoiceField(
        label="Grupo (opcional)", queryset=Classroom.objects.none(), required=False
    )
    new_group = forms.CharField(
        label="O crea un grupo aquí", max_length=100, required=False
    )

    def __init__(self, *args, operator, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator = operator
        self.fields["classroom"].queryset = classrooms_for(operator).filter(
            teacher=operator, active=True
        )

    def clean(self):
        data = super().clean()
        if data.get("classroom") and data.get("new_group"):
            raise forms.ValidationError(
                "Elige un grupo existente o escribe uno nuevo, no ambos."
            )
        return data

    def group(self):
        if self.cleaned_data.get("new_group"):
            return Classroom.objects.create(
                name=self.cleaned_data["new_group"], teacher=self.operator
            )
        return self.cleaned_data.get("classroom")


class StudentCreateForm(GroupChoiceForm):
    name = forms.CharField(label="Nombre o alias", max_length=150)
    age = forms.IntegerField(label="Edad", min_value=6, max_value=14)
    field_order = ["name", "age", "classroom", "new_group"]

    @transaction.atomic
    def save(self):
        import uuid
        from progreso.services.progress import category_for_age

        student = Student.objects.create(
            name=self.cleaned_data["name"],
            age=self.cleaned_data["age"],
            category=category_for_age(self.cleaned_data["age"]),
            teacher=self.operator,
            claim_code=uuid.uuid4().hex,
        )
        group = self.group()
        if group:
            student.classrooms.add(group)
        return student


class PupilRowForm(forms.Form):
    name = forms.CharField(label="Nombre o alias", max_length=150)
    age = forms.IntegerField(label="Edad", min_value=6, max_value=14)


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "age", "category", "difficulty", "classrooms", "active"]

    def __init__(self, *args, operator, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["classrooms"].queryset = classrooms_for(operator).filter(
            teacher=self.instance.teacher
        )
        self.independent = self.instance.self_registered and not operator.is_superuser
        if self.independent:
            self.fields.pop("active")
            self.fields["name"].disabled = True
            self.fields["age"].disabled = True

    @transaction.atomic
    def save(self, commit=True):
        student = super().save(commit)
        if student.user_id and not self.independent:
            student.user.first_name = student.name
            student.user.is_active = student.active
            student.user.save()
        from progreso.services.progress import worlds

        worlds(student)
        return student


class JoinGroupForm(forms.Form):
    group_code = forms.CharField(
        label="Código de tu profesor", max_length=12, min_length=12
    )

    def clean_group_code(self):
        return self.cleaned_data["group_code"].strip().upper()


class ClaimProfileForm(forms.Form):
    code = forms.CharField(
        label="Código personal del profesor",
        max_length=32,
        min_length=32,
        help_text="Vincula tu cuenta al perfil de clase y combina los progresos. Este código personal es distinto al código de grupo.",
    )


PupilFormSet = forms.formset_factory(
    PupilRowForm,
    extra=5,
    max_num=100,
    validate_max=True,
    absolute_max=100,
    min_num=1,
    validate_min=True,
)
