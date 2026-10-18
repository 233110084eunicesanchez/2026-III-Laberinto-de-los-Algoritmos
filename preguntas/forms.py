from django import forms
from preguntas.models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "subject",
            "category",
            "difficulty",
            "topic",
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct",
            "explanation",
        ]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "explanation": forms.Textarea(attrs={"rows": 3}),
        }
