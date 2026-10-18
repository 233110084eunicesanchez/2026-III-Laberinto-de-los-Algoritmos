from django.urls import path
from . import views as v

app_name = "inicio"
urlpatterns = [
    path("", v.HomeView.as_view(), name="home"),
]
