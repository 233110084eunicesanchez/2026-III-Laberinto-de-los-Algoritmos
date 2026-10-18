from django.urls import path
from . import views as v

app_name = "escuela"
urlpatterns = [
    path("alumnos/lote/", v.BulkStudentsView.as_view(), name="bulk_students"),
    path("vincular/", v.ClaimProfileView.as_view(), name="claim_profile"),
    path("unirme/", v.JoinGroupView.as_view(), name="join_group"),
    path(
        "grupos/<int:pk>/codigo/",
        v.RotateInvitationView.as_view(),
        name="rotate_invitation",
    ),
    path("grupos/", v.ClassroomList.as_view(), name="classrooms"),
    path("grupos/nuevo/", v.ClassroomCreate.as_view(), name="classroom_create"),
    path("grupos/<int:pk>/", v.ClassroomDetail.as_view(), name="classroom_detail"),
    path(
        "grupos/<int:pk>/editar/", v.ClassroomUpdate.as_view(), name="classroom_update"
    ),
    path(
        "grupos/<int:pk>/eliminar/",
        v.ClassroomDelete.as_view(),
        name="classroom_delete",
    ),
    path("alumnos/", v.StudentList.as_view(), name="students"),
    path("alumnos/nuevo/", v.StudentCreate.as_view(), name="student_create"),
    path("alumnos/<int:pk>/", v.StudentDetail.as_view(), name="student_detail"),
    path("alumnos/<int:pk>/editar/", v.StudentUpdate.as_view(), name="student_update"),
    path(
        "alumnos/<int:pk>/eliminar/", v.StudentDelete.as_view(), name="student_delete"
    ),
]
