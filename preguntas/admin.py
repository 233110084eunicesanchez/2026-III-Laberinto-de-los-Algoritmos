from django.contrib import admin
from .models import Question, Subject, Category


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "category", "difficulty", "topic", "status", "author"]
    list_filter = ["category", "difficulty", "status", "topic"]
    search_fields = ["text"]

    @admin.action(description="Publicar preguntas seleccionadas")
    def publish(self, request, qs):
        for q in qs:
            q.full_clean()
            q.status = "published"
            q.save()

    actions = [publish]


admin.site.register(Subject)
admin.site.register(Category)
