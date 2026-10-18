from django.urls import path
from . import views as v

app_name = "preguntas"
urlpatterns = [
    path("preguntas/", v.QuestionList.as_view(), name="questions"),
    path("preguntas/nueva/", v.QuestionCreate.as_view(), name="question_create"),
    path("preguntas/<int:pk>/", v.QuestionDetail.as_view(), name="question_detail"),
    path(
        "preguntas/<int:pk>/editar/", v.QuestionUpdate.as_view(), name="question_update"
    ),
    path(
        "preguntas/<int:pk>/eliminar/",
        v.QuestionDelete.as_view(),
        name="question_delete",
    ),
    path("preguntas/<int:pk>/publicar/", v.PublishView.as_view(), name="publish"),
]
