from django.test import TestCase, Client, override_settings
from django.core.management import call_command
from django.contrib.auth.models import Group
from django.urls import reverse
from .models import User, Student, Category, Classroom
from .services.accounts import join_group

@override_settings(SECURE_SSL_REDIRECT=False,STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class RegistrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_initial',verbosity=0)
        cls.teacher=User.objects.create_user('teacher',password='Teacher-test-2026')
        cls.teacher.groups.add(Group.objects.get(name='Profesor'))
        cls.other=User.objects.create_user('other',password='Teacher-test-2026')
        cls.other.groups.add(Group.objects.get(name='Profesor'))
        cls.room=Classroom.objects.create(teacher=cls.teacher,name='Robots')
        cls.other_room=Classroom.objects.create(teacher=cls.other,name='Estrellas')
    def data(self,**extra):
        return {'email':'tutor@example.test','username':'newuser','first_name':'Explorador','role':'student','age':10,'password1':'A-secure-test-123','password2':'A-secure-test-123',**extra}
    def signup(self,**extra):return self.client.post(reverse('cuentas:register'),self.data(**extra))
    def test_student_registers_independently_and_starts_practice(self):
        r=self.signup();self.assertRedirects(r,reverse('inicio:home'))
        u=User.objects.get(username='newuser');s=u.student
        self.assertEqual(s.category.code,'BETA');self.assertIsNone(s.teacher);self.assertTrue(s.self_registered)
        self.assertTrue(u.groups.filter(name='Alumno').exists());self.assertEqual(str(u.pk),self.client.session['_auth_user_id'])
        self.assertEqual(self.client.post(reverse('juego:start')).status_code,302)
        self.assertEqual(s.attempts.get().mode,'solo')
    def test_age_boundaries(self):
        for age,category in [(6,'ALFA'),(8,'ALFA'),(9,'BETA'),(11,'BETA'),(12,'OMEGA'),(14,'OMEGA')]:
            self.client.logout();self.signup(username=f'age{age}',age=age)
            self.assertEqual(User.objects.get(username=f'age{age}').student.category.code,category)
    def test_teacher_registers_without_age_and_without_approval(self):
        r=self.signup(role='teacher',age='');self.assertRedirects(r,reverse('inicio:home'))
        u=User.objects.get(username='newuser');self.assertTrue(u.has_perm('juego.conduct_attempt'))
        self.assertFalse(u.is_staff);self.assertFalse(u.is_superuser);self.assertFalse(Student.objects.filter(user=u).exists())
        self.assertContains(self.client.get(reverse('inicio:home')),'Mis grupos')
        self.assertEqual(self.client.post(reverse('escuela:classroom_create'),{'name':'Mi grupo','active':'on'}).status_code,302)
        self.assertEqual(Classroom.objects.get(name='Mi grupo').teacher,u)
        self.assertNotContains(self.client.get(reverse('escuela:classrooms')),'Robots')
    def test_mass_assignment_cannot_create_admin(self):
        self.signup(role='teacher',age='',is_staff='true',is_superuser='true',groups='Administrador',user_permissions='*')
        u=User.objects.get(username='newuser');self.assertFalse(u.is_staff);self.assertFalse(u.is_superuser)
        self.assertEqual(list(u.groups.values_list('name',flat=True)),['Profesor'])
        self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_invalid_role_age_and_duplicate_name(self):
        for fields in [{'role':'admin'},{'age':''},{'age':5},{'age':15},{'username':'TEACHER'}]:
            self.assertEqual(self.signup(**fields).status_code,200)
            self.assertFalse(User.objects.filter(username='newuser').exists())
    def test_passwords_validated(self):
        self.assertEqual(self.signup(password1='123',password2='123').status_code,200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
    def test_invalid_code_does_not_leave_partial_account(self):
        self.assertEqual(self.signup(group_code='DOESNOTEXIST').status_code,200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
    def test_optional_code_links_to_correct_teacher(self):
        self.assertEqual(self.signup(group_code=self.room.invite_code.lower()).status_code,302)
        s=User.objects.get(username='newuser').student
        self.assertEqual(s.teacher,self.teacher);self.assertTrue(s.classrooms.filter(pk=self.room.pk).exists())
        self.client.force_login(self.other);self.assertEqual(self.client.get(reverse('escuela:student_detail',args=[s.pk])).status_code,404)
    def test_join_after_independent_registration_and_duplicate_join(self):
        self.signup();s=User.objects.get(username='newuser').student
        for _ in range(2):self.assertEqual(self.client.post(reverse('escuela:join_group'),{'group_code':self.room.invite_code}).status_code,302)
        s.refresh_from_db();self.assertEqual(s.teacher,self.teacher);self.assertEqual(s.classrooms.count(),1)
    def test_cannot_silently_transfer_between_teachers(self):
        self.signup(group_code=self.room.invite_code)
        self.assertEqual(self.client.post(reverse('escuela:join_group'),{'group_code':self.other_room.invite_code}).status_code,200)
        self.assertEqual(User.objects.get(username='newuser').student.teacher,self.teacher)
    def test_archived_group_or_disabled_teacher_cannot_receive_signup(self):
        self.room.active=False;self.room.save()
        self.assertEqual(self.signup(group_code=self.room.invite_code).status_code,200)
        self.room.active=True;self.room.save();self.teacher.is_active=False;self.teacher.save()
        self.assertEqual(self.signup(group_code=self.room.invite_code).status_code,200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
    def test_independent_student_can_be_removed_without_losing_account(self):
        self.signup(group_code=self.room.invite_code);u=User.objects.get(username='newuser')
        self.client.force_login(self.teacher);self.client.post(reverse('escuela:student_delete',args=[u.student.pk]))
        u.refresh_from_db();self.assertTrue(u.is_active);self.assertIsNone(u.student.teacher)
        self.assertEqual(u.student.classrooms.count(),0)
    def test_teacher_cannot_disable_self_registered_account_via_edit(self):
        self.signup(group_code=self.room.invite_code);u=User.objects.get(username='newuser');s=u.student
        self.client.force_login(self.teacher)
        r=self.client.post(reverse('escuela:student_update',args=[s.pk]),{'first_name':'Changed','age':7,'category':s.category_id,'difficulty':2,'classrooms':[self.room.pk]})
        self.assertEqual(r.status_code,302);u.refresh_from_db();s.refresh_from_db()
        self.assertTrue(u.is_active);self.assertTrue(s.active);self.assertEqual(s.age,10);self.assertEqual(u.first_name,'Explorador');self.assertEqual(s.difficulty,2)
    def test_rotation_is_scoped_and_invalidates_old_code(self):
        old=self.room.invite_code;self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('escuela:rotate_invitation',args=[self.room.pk])).status_code,404)
        self.client.force_login(self.teacher);self.client.post(reverse('escuela:rotate_invitation',args=[self.room.pk]))
        self.room.refresh_from_db();self.assertNotEqual(old,self.room.invite_code)
        self.client.logout();self.assertEqual(self.signup(group_code=old).status_code,200)
    def test_csrf_and_no_second_registration_when_authenticated(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post(reverse('cuentas:register'),self.data()).status_code,403)
        self.signup();self.assertRedirects(self.client.get(reverse('cuentas:register')),reverse('inicio:home'))
        self.assertRedirects(self.client.get(reverse('cuentas:login')),reverse('inicio:home'))
    def test_navigation_reflects_role_and_login_offers_registration(self):
        self.assertContains(self.client.get(reverse('cuentas:login')),reverse('cuentas:register'))
        self.assertEqual(self.client.get(reverse('cuentas:register')).status_code,200)
        self.signup();home=self.client.get(reverse('inicio:home'))
        self.assertNotContains(home,'Mis grupos');self.assertNotContains(home,'Administración')
        self.assertContains(home,'BETA');self.assertContains(home,reverse('escuela:join_group'))
    def test_authenticated_student_cannot_change_role_by_posting_registration(self):
        self.signup();self.client.post(reverse('cuentas:register'),self.data(role='teacher',username='escalated'))
        self.assertFalse(User.objects.filter(username='escalated').exists())
        self.assertFalse(User.objects.get(username='newuser').has_perm('juego.conduct_attempt'))
