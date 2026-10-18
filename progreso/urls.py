from django.urls import path
from . import views as v

app_name = "progreso"
urlpatterns = [
    path("mision/<uuid:pk>/resultado/", v.ResultView.as_view(), name="result"),
    path("historial/", v.History.as_view(), name="history"),
]
