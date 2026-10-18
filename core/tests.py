import json, random
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, override_settings, Client
from django.core.management import call_command
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from .models import User, Student, Classroom, Category, Question, Attempt
from .services import game
from .services.maze import generate, paths, neighbors
from .services.question_bank import bank

@override_settings(SECURE_SSL_REDIRECT=False,STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class ProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_initial',verbosity=0)
        cls.teacher=User.objects.create_user('teacher',password='Teacher-test-2026')
        cls.teacher.groups.add(Group.objects.get(name='Profesor'))
        cls.other=User.objects.create_user('other',password='Other-test-2026')
        cls.other.groups.add(Group.objects.get(name='Profesor'))
        cls.admin=User.objects.create_superuser('admin','',password='Admin-test-2026')
        cls.child=User.objects.create_user('child',password='Child-test-2026')
        cls.child.groups.add(Group.objects.get(name='Alumno'))
        cls.student=Student.objects.create(user=cls.child,teacher=cls.teacher,age=7,category=Category.objects.get(code='ALFA'))
        cls.room=Classroom.objects.create(name='Exploradores',teacher=cls.teacher)
        cls.foreign_room=Classroom.objects.create(name='Otro grupo',teacher=cls.other)
    def attempt(self,mode='mission'):
        return game.create_attempt(self.student,self.teacher if mode=='mission' else self.child,mode)
    def settle(self,a):
        a.refresh_from_db()
        game.status(a.pk)
        a.refresh_from_db()
    def test_bank_counts_distinctness_and_options(self):
        data=list(bank())
        self.assertEqual(len(data),360);self.assertEqual(len({q['text'] for q in data}),360)
        for code in ['ALFA','BETA','OMEGA']:
            for difficulty in [1,2,3]:
                self.assertEqual(Question.objects.filter(category__code=code,difficulty=difficulty).count(),40)
        for q in Question.objects.all():q.full_clean();self.assertEqual(len(set(q.options)),4)
    def test_seed_is_idempotent_and_preserves_edits(self):
        q=Question.objects.first();q.text='Una pregunta editada';q.save()
        call_command('seed_initial',verbosity=0);q.refresh_from_db()
        self.assertEqual(q.text,'Una pregunta editada');self.assertEqual(Question.objects.count(),360)
    def test_three_hundred_valid_mazes(self):
        for code,count,minlen in [('ALFA',2,7),('BETA',2,9),('OMEGA',1,11)]:
            goals=set()
            for i in range(100):
                board=generate(code,random.Random(i));safe=set(board['safe'])
                routes=paths(safe,board['goal']);self.assertEqual(len(routes),count)
                self.assertGreaterEqual(min(map(len,routes)),minlen)
                self.assertNotEqual(board['goal'],0);goals.add(board['goal'])
                for route in routes:
                    for a,b in zip(route,route[1:]):self.assertIn(b,neighbors(a))
            self.assertGreater(len(goals),8)
    def test_all_score_thresholds_and_five_questions(self):
        for score in range(6):
            a=self.attempt('practice');game.action(a.pk,'start')
            for i in range(5):
                item=a.items.get(position=i)
                answer=item.snapshot['correct'] if i<score else (item.snapshot['correct']+1)%4
                game.action(a.pk,'answer',i,answer);self.settle(a)
            self.assertEqual(a.score,score);self.assertEqual(a.state,'won' if score>=3 else 'lost')
            self.assertEqual(a.items.filter(answered_at__isnull=False).count(),5)
    def test_virus_has_no_math_grade(self):
        a=self.attempt();game.action(a.pk,'start');game.action(a.pk,'virus');a.refresh_from_db()
        self.assertEqual(a.state,'virus');self.assertFalse(a.items.filter(answered_at__isnull=False).exists())
    def test_cannot_skip_board(self):
        a=self.attempt();game.action(a.pk,'goal');a.refresh_from_db();self.assertEqual(a.state,'ready')
        game.action(a.pk,'answer',0,0);a.refresh_from_db();self.assertEqual(a.score,0)
    def test_timeout_is_not_an_answer_and_reload_does_not_reset(self):
        self.student.age=10;self.student.category=Category.objects.get(code='BETA');self.student.save()
        a=self.attempt('practice');game.action(a.pk,'start');a.refresh_from_db();deadline=a.deadline
        game.status(a.pk);a.refresh_from_db();self.assertEqual(a.deadline,deadline)
        with patch('core.services.game.timezone.now',return_value=deadline+timedelta(seconds=1)):
            game.action(a.pk,'answer',0,a.items.first().snapshot['correct'])
        item=a.items.first();self.assertIsNone(item.selected);self.assertFalse(item.correct)
    def test_duplicate_and_stale_answers_do_not_double_score(self):
        a=self.attempt('practice');game.action(a.pk,'start');answer=a.items.first().snapshot['correct']
        game.action(a.pk,'answer',0,answer);game.action(a.pk,'answer',0,answer)
        self.settle(a);game.action(a.pk,'answer',0,answer);a.refresh_from_db()
        self.assertEqual(a.current,1);self.assertEqual(a.score,1)
    def test_snapshots_survive_question_changes(self):
        a=self.attempt();item=a.items.first();text=item.snapshot['text'];q=item.question
        q.text='Texto cambiado';q.correct=(q.correct+1)%4;q.save();item.refresh_from_db()
        self.assertEqual(item.snapshot['text'],text)
    def test_api_does_not_leak_correct_answer(self):
        a=self.attempt('practice');game.action(a.pk,'start');self.client.force_login(self.child)
        data=self.client.get(reverse('juego:api_status',args=[a.pk])).json()
        self.assertNotIn('correct',data['question']);self.assertNotIn('explanation',data['question'])
    def test_teacher_cannot_access_another_teachers_student(self):
        self.client.force_login(self.other)
        for name in ['escuela:student_detail', 'escuela:student_update', 'escuela:student_delete']:
            self.assertEqual(self.client.get(reverse(name,args=[self.student.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('juego:start'),{'student':self.student.pk}).status_code,404)
        a=self.attempt()
        for name in ['juego:play', 'juego:api_status', 'progreso:result']:
            self.assertEqual(self.client.get(reverse(name,args=[a.pk])).status_code,404)
    def test_student_cannot_manage_or_operate_mission(self):
        self.client.force_login(self.child)
        self.assertEqual(self.client.get(reverse('escuela:student_create')).status_code,403)
        self.assertEqual(self.client.get(reverse('preguntas:questions')).status_code,403)
        a=self.attempt()
        self.assertEqual(self.client.post(reverse('juego:api_action',args=[a.pk]),json.dumps({'command':'start'}),content_type='application/json').status_code,403)
    def test_student_start_always_uses_own_profile(self):
        self.client.force_login(self.child)
        self.client.post(reverse('juego:start'),{'student':999,'mode':'mission'})
        a=Attempt.objects.get();self.assertEqual(a.mode,'mission');self.assertEqual(a.student,self.student)
    def test_double_start_reuses_active_attempt(self):
        self.client.force_login(self.teacher)
        for _ in range(2):self.client.post(reverse('juego:start'),{'student':self.student.pk})
        self.assertEqual(Attempt.objects.count(),1)
    def test_permissions_revocation_is_enforced(self):
        self.teacher.groups.clear();self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('escuela:classrooms')).status_code,403)
    def test_teacher_cannot_publish_or_change_others_question(self):
        self.client.force_login(self.teacher);q=Question.objects.first()
        self.assertEqual(self.client.post(reverse('preguntas:publish',args=[q.pk])).status_code,403)
        self.assertEqual(self.client.get(reverse('preguntas:question_update',args=[q.pk])).status_code,404)
    def test_foreign_classroom_rejected_in_student_form(self):
        self.client.force_login(self.teacher)
        r=self.client.post(reverse('escuela:student_create'),{'name':'Nuevo','age':8,'classroom':self.foreign_room.pk})
        self.assertEqual(r.status_code,200);self.assertFalse(User.objects.filter(username='newchild').exists())
    def test_create_school_profile_without_login(self):
        self.client.force_login(self.teacher)
        r=self.client.post(reverse('escuela:student_create'),{'name':'Nuevo','age':8,'classroom':self.room.pk})
        self.assertEqual(r.status_code,302)
        s=Student.objects.get(name='Nuevo');self.assertIsNone(s.user_id);self.assertEqual(s.teacher,self.teacher)
        self.assertTrue(s.classrooms.filter(pk=self.room.pk).exists());self.assertEqual(len(s.claim_code),32)
    def test_question_delete_with_history_retires(self):
        a=self.attempt();q=a.items.first().question;self.client.force_login(self.admin)
        self.client.post(reverse('preguntas:question_delete',args=[q.pk]));q.refresh_from_db();self.assertEqual(q.status,'retired')
    def test_student_delete_preserves_history_and_disables_login(self):
        self.attempt();self.client.force_login(self.teacher)
        self.client.post(reverse('escuela:student_delete',args=[self.student.pk]));self.child.refresh_from_db()
        self.assertFalse(self.child.is_active);self.assertEqual(Attempt.objects.count(),1)
    def test_csrf_required_for_mutations(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.teacher)
        self.assertEqual(client.post(reverse('juego:start'),{'student':self.student.pk}).status_code,403)
    def test_public_screen_readonly_no_names_no_solution(self):
        a=self.attempt();game.action(a.pk,'start')
        d=self.client.get(reverse('juego:display_status',args=[a.display_token])).json()
        self.assertNotIn('student',d);self.assertNotIn('routes',d['board'])
        self.assertEqual(self.client.post(reverse('juego:api_action',args=[a.pk]),{'command':'goal'}).status_code,302)
    def test_insufficient_questions_does_not_create_attempt(self):
        Question.objects.filter(category=self.student.category).update(status='retired')
        with self.assertRaises(ValueError):self.attempt()
        self.assertEqual(Attempt.objects.count(),0)
    def test_authenticated_pages_render(self):
        self.client.force_login(self.teacher)
        for name in ['inicio:home', 'escuela:classrooms', 'escuela:students', 'preguntas:questions', 'cuentas:profile', 'progreso:history', 'escuela:student_create', 'preguntas:question_create', 'escuela:classroom_create', 'cuentas:password_change']:
            with self.subTest(name=name):self.assertEqual(self.client.get(reverse(name)).status_code,200)
        self.client.force_login(self.child)
        for name in ['inicio:home', 'cuentas:profile', 'progreso:history']:self.assertEqual(self.client.get(reverse(name)).status_code,200)
        a=self.attempt('practice');self.assertEqual(self.client.get(reverse('juego:play',args=[a.pk])).status_code,200)

    def test_staff_teacher_cannot_bypass_scope_using_admin(self):
        self.teacher.is_staff=True;self.teacher.save();self.client.force_login(self.teacher)
        r=self.client.get('/admin/core/student/')
        self.assertEqual(r.status_code,302);self.assertIn('/admin/login/',r.url)
