from django.urls import path
from . import views as v

app_name = "juego"
urlpatterns = [
    path("mundos/<str:code>/", v.ChooseModeView.as_view(), name="choose_mode"),
    path("iniciar/", v.StartView.as_view(), name="start"),
    path("mision/<uuid:pk>/", v.PlayView.as_view(), name="play"),
    path("mision/<uuid:pk>/estado/", v.ApiStatusView.as_view(), name="api_status"),
    path("mision/<uuid:pk>/accion/", v.ApiActionView.as_view(), name="api_action"),
    path("mision/<uuid:pk>/reintentar/", v.RetryView.as_view(), name="retry"),
    path("pantalla/<uuid:token>/", v.DisplayView.as_view(), name="display"),
    path(
        "pantalla/<uuid:token>/estado/",
        v.DisplayStatusView.as_view(),
        name="display_status",
    ),
]
