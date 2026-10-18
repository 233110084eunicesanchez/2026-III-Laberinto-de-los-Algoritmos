"""Regresiones de acceso roto y migración de apps sobre datos existentes."""

import json
from datetime import timedelta
from django.test import TestCase, TransactionTestCase, Client, override_settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import get_resolver, URLResolver, reverse
from django.utils import timezone
from core.models import User
from escuela.models import Student, Classroom
from preguntas.models import Category, Question
from juego.models import Attempt
from juego.services import game

TEST_SETTINGS = dict(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)


@override_settings(**TEST_SETTINGS)
class ModularAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_initial", verbosity=0)
        cls.alfa = Category.objects.get(code="ALFA")
        cls.teacher = User.objects.create_user("mod_teacher")
        cls.other = User.objects.create_user("mod_other")
        for user in [cls.teacher, cls.other]:
            user.groups.add(Group.objects.get(name="Profesor"))
        cls.child = User.objects.create_user("mod_child")
        cls.child.groups.add(Group.objects.get(name="Alumno"))
        cls.student = Student.objects.create(
            user=cls.child, name="A", age=7, category=cls.alfa, teacher=cls.teacher
        )
        cls.room = Classroom.objects.create(name="Privado", teacher=cls.teacher)
        cls.student.classrooms.add(cls.room)
        cls.question = Question.objects.filter(category=cls.alfa).first()
        cls.question.author = cls.teacher
        cls.question.save()

    def test_every_application_endpoint_is_class_based_and_namespaced(self):
        domains = {"cuentas", "inicio", "escuela", "preguntas", "juego", "progreso"}
        seen = set()
        for resolver in get_resolver().url_patterns:
            if isinstance(resolver, URLResolver) and resolver.namespace in domains:
                seen.add(resolver.namespace)
                for route in resolver.url_patterns:
                    with self.subTest(route=str(route.pattern)):
                        self.assertIsNotNone(
                            getattr(route.callback, "view_class", None)
                        )
        self.assertEqual(seen, domains)

    def test_teachers_cannot_read_or_modify_other_teachers_objects(self):
        self.client.force_login(self.other)
        for name, pk in [
            ("escuela:student_detail", self.student.pk),
            ("escuela:student_update", self.student.pk),
            ("escuela:student_delete", self.student.pk),
            ("escuela:classroom_detail", self.room.pk),
            ("escuela:classroom_update", self.room.pk),
            ("escuela:classroom_delete", self.room.pk),
            ("preguntas:question_detail", self.question.pk),
            ("preguntas:question_update", self.question.pk),
            ("preguntas:question_delete", self.question.pk),
        ]:
            for method in ["get", "post"]:
                with self.subTest(name=name, method=method):
                    expected = (
                        405 if method == "post" and name.endswith("_detail") else 404
                    )
                    self.assertEqual(
                        getattr(self.client, method)(
                            reverse(name, args=[pk])
                        ).status_code,
                        expected,
                    )
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())

    def test_students_cannot_manage_school_or_publish(self):
        self.client.force_login(self.child)
        for name in [
            "escuela:classroom_create",
            "escuela:student_create",
            "escuela:bulk_students",
            "preguntas:question_create",
        ]:
            self.assertEqual(self.client.post(reverse(name), {}).status_code, 403)
        self.assertEqual(
            self.client.post(
                reverse("preguntas:publish", args=[self.question.pk])
            ).status_code,
            403,
        )

    def test_forged_teacher_and_status_fields_do_not_escalate(self):
        self.client.force_login(self.other)
        self.client.post(
            reverse("escuela:classroom_create"),
            {"name": "Nuevo", "active": "on", "teacher": self.teacher.pk},
        )
        self.assertEqual(Classroom.objects.get(name="Nuevo").teacher_id, self.other.pk)
        data = {
            f: getattr(self.question, f)
            for f in [
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
        }
        data.update(
            subject=self.question.subject_id,
            category=self.alfa.pk,
            status="published",
            author=self.teacher.pk,
        )
        self.assertEqual(
            self.client.post(reverse("preguntas:question_create"), data).status_code,
            302,
        )
        q = Question.objects.order_by("-pk").first()
        self.assertEqual(q.author_id, self.other.pk)
        self.assertEqual(q.status, "draft")

    def test_teacher_can_observe_but_cannot_control_student_operated_attempt(self):
        a = game.create_attempt(self.student, self.child, "solo")
        self.client.force_login(self.teacher)
        self.assertEqual(
            self.client.get(reverse("juego:play", args=[a.pk])).status_code, 200
        )
        self.assertEqual(
            self.client.post(
                reverse("juego:api_action", args=[a.pk]),
                json.dumps({"command": "start"}),
                content_type="application/json",
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(reverse("juego:retry", args=[a.pk])).status_code, 403
        )
        a.refresh_from_db()
        self.assertEqual(a.state, "ready")

    def test_other_teacher_cannot_access_any_attempt_endpoint(self):
        a = game.create_attempt(self.student, self.child, "solo")
        self.client.force_login(self.other)
        for name in ["juego:play", "juego:api_status", "progreso:result"]:
            self.assertEqual(
                self.client.get(reverse(name, args=[a.pk])).status_code, 404
            )
        for name in ["juego:api_action", "juego:retry"]:
            self.assertEqual(
                self.client.post(
                    reverse(name, args=[a.pk]), "{}", content_type="application/json"
                ).status_code,
                404,
            )

    def test_revoked_student_role_fails_closed(self):
        a = game.create_attempt(self.student, self.child, "solo")
        self.child.groups.clear()
        self.client.force_login(self.child)
        self.assertEqual(
            self.client.get(reverse("juego:api_status", args=[a.pk])).status_code, 404
        )
        self.assertEqual(
            self.client.post(reverse("juego:start"), {"category": "ALFA"}).status_code,
            404,
        )

    def test_revoked_teacher_read_permission_blocks_attempt_access(self):
        a = game.create_attempt(self.student, self.teacher, "mission")
        group = Group.objects.get(name="Profesor")
        group.permissions.remove(
            Permission.objects.get(
                content_type__app_label="juego", codename="view_attempt"
            )
        )
        self.client.force_login(self.teacher)
        self.assertEqual(
            self.client.get(reverse("juego:api_status", args=[a.pk])).status_code, 404
        )
        self.assertEqual(
            self.client.post(
                reverse("juego:api_action", args=[a.pk]),
                "{}",
                content_type="application/json",
            ).status_code,
            404,
        )

    def test_get_cannot_perform_mutations(self):
        self.client.force_login(self.teacher)
        a = game.create_attempt(self.student, self.teacher, "mission")
        for name, args in [
            ("juego:start", []),
            ("juego:api_action", [a.pk]),
            ("juego:retry", [a.pk]),
            ("escuela:rotate_invitation", [self.room.pk]),
        ]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 405)

    def test_invalid_json_shapes_return_400_without_mutation(self):
        self.client.force_login(self.child)
        a = game.create_attempt(self.student, self.child, "solo")
        for body in [
            "[]",
            "null",
            '"x"',
            "{",
            json.dumps({"command": "answer", "position": True, "selected": 0}),
        ]:
            self.assertEqual(
                self.client.post(
                    reverse("juego:api_action", args=[a.pk]),
                    body,
                    content_type="application/json",
                ).status_code,
                400,
            )
        a.refresh_from_db()
        self.assertEqual(a.state, "ready")

    def test_csrf_is_required_even_for_authenticated_game_actions(self):
        a = game.create_attempt(self.student, self.child, "solo")
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.child)
        self.assertEqual(
            c.post(
                reverse("juego:api_action", args=[a.pk]),
                "{}",
                content_type="application/json",
            ).status_code,
            403,
        )

    def test_projection_is_readonly_anonymous_and_expires(self):
        a = game.create_attempt(self.student, self.teacher, "mission")
        game.action(a.pk, "start")
        url = reverse("juego:display_status", args=[a.display_token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn("routes", data["board"])
        self.assertNotIn("student", data)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(self.client.post(url, {}).status_code, 405)
        Attempt.objects.filter(pk=a.pk).update(
            created_at=timezone.now() - timedelta(hours=9)
        )
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_start_reuses_active_attempt_and_admin_retains_access(self):
        self.client.force_login(self.child)
        for _ in range(2):
            self.client.post(
                reverse("juego:start"), {"category": "ALFA", "mode": "solo"}
            )
        self.assertEqual(Attempt.objects.filter(student=self.student).count(), 1)
        admin = User.objects.create_superuser("mod_admin", "", password="Testing-2026")
        self.client.force_login(admin)
        self.assertEqual(
            self.client.get(
                reverse("escuela:student_detail", args=[self.student.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                reverse("preguntas:publish", args=[self.question.pk])
            ).status_code,
            302,
        )


class DomainMigrationTests(TransactionTestCase):
    def test_content_type_ids_permissions_passwords_and_memberships_survive(self):
        before = [("core", "0005_world_names")]
        after = [("core", "0006_domain_apps")]
        MigrationExecutor(connection).migrate(before)
        try:
            executor = MigrationExecutor(connection)
            old = executor.loader.project_state(before).apps
            U = old.get_model("core", "User")
            C = old.get_model("core", "Category")
            S = old.get_model("core", "Student")
            Room = old.get_model("core", "Classroom")
            CT = old.get_model("contenttypes", "ContentType")
            P = old.get_model("auth", "Permission")
            G = old.get_model("auth", "Group")
            teacher = U.objects.create(
                username="migrated-teacher", password="unchanged-hash"
            )
            child = U.objects.create(username="migrated-child", password="child-hash")
            cat = C.objects.create(
                code="ALFA",
                name="Nombre personalizado",
                min_age=6,
                max_age=8,
                seconds=0,
                routes=2,
            )
            student = S.objects.create(
                user=child, teacher=teacher, name="Conservar", age=7, category=cat
            )
            room = Room.objects.create(name="Conservar grupo", teacher=teacher)
            student.classrooms.add(room)
            ct, _ = CT.objects.get_or_create(app_label="core", model="student")
            perm, _ = P.objects.get_or_create(
                content_type=ct,
                codename="change_student",
                defaults={"name": "Editar alumno"},
            )
            group = G.objects.create(name="Grupo personalizado")
            group.permissions.add(perm)
            teacher.groups.add(group)
            teacher.user_permissions.add(perm)
            ids = (teacher.pk, child.pk, student.pk, room.pk, ct.pk, perm.pk, group.pk)
            MigrationExecutor(connection).migrate(after)
            t = User.objects.get(pk=ids[0])
            self.assertEqual(t.password, "unchanged-hash")
            self.assertTrue(t.has_perm("escuela.change_student"))
            self.assertFalse(t.has_perm("core.change_student"))
            self.assertEqual(
                ContentType.objects.get(app_label="escuela", model="student").pk, ids[4]
            )
            self.assertEqual(Permission.objects.get(pk=ids[5]).content_type_id, ids[4])
            self.assertTrue(t.user_permissions.filter(pk=ids[5]).exists())
            self.assertTrue(
                Group.objects.get(pk=ids[6]).permissions.filter(pk=ids[5]).exists()
            )
            s = Student.objects.get(pk=ids[2])
            self.assertEqual(s.user_id, ids[1])
            self.assertTrue(s.classrooms.filter(pk=ids[3]).exists())
            self.assertEqual(s.category.name, "Nombre personalizado")
            self.assertEqual(Student._meta.db_table, "core_student")
        finally:
            MigrationExecutor(connection).migrate(after)
