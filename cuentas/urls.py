from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth
from . import views as v

app_name = "cuentas"
urlpatterns = [
    path(
        "cuenta/login/",
        auth.LoginView.as_view(
            template_name="cuentas/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("cuenta/registro/", v.RegisterView.as_view(), name="register"),
    path(
        "cuenta/recuperar/",
        auth.PasswordResetView.as_view(
            email_template_name="cuentas/password_reset_email.html",
            subject_template_name="cuentas/password_reset_subject.txt",
            template_name="cuentas/password_reset_form.html",
            success_url=reverse_lazy("cuentas:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "cuenta/recuperar/enviado/",
        auth.PasswordResetDoneView.as_view(
            template_name="cuentas/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "cuenta/restablecer/<uidb64>/<token>/",
        auth.PasswordResetConfirmView.as_view(
            template_name="cuentas/password_reset_confirm.html",
            success_url=reverse_lazy("cuentas:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "cuenta/restablecer/listo/",
        auth.PasswordResetCompleteView.as_view(
            template_name="cuentas/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("cuenta/logout/", auth.LogoutView.as_view(), name="logout"),
    path(
        "cuenta/password_change/",
        auth.PasswordChangeView.as_view(
            template_name="cuentas/password_change_form.html",
            success_url=reverse_lazy("cuentas:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "cuenta/password_change/done/",
        auth.PasswordChangeDoneView.as_view(
            template_name="cuentas/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path("perfil/", v.ProfileView.as_view(), name="profile"),
]
