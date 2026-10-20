"""Regresiones de progresión, perfiles escolares y las dos modalidades."""
import json, uuid, random
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, TransactionTestCase, override_settings
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core import mail
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from core.models import User, Student, Category, Question, Classroom, Attempt, Mastery, WorldUnlock
from core.services import game
from core.services.progress import worlds, can_play, learning_tier
from core.services.accounts import claim_profile
from core.services.maze import generate, neighbors, paths, crash_path

@override_settings(SECURE_SSL_REDIRECT=False,EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class VersionTwoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_initial',verbosity=0)
        cls.teacher=User.objects.create_user('teacher',email='teacher@example.test',password='Teacher-test-2026')
        cls.teacher.groups.add(Group.objects.get(name='Profesor'))
        cls.other=User.objects.create_user('other',password='Teacher-test-2026');cls.other.groups.add(Group.objects.get(name='Profesor'))
        cls.user=User.objects.create_user('child',password='Child-test-2026');cls.user.groups.add(Group.objects.get(name='Alumno'))
        cls.alfa=Category.objects.get(code='ALFA');cls.beta=Category.objects.get(code='BETA');cls.omega=Category.objects.get(code='OMEGA')
        cls.student=Student.objects.create(user=cls.user,name='Explorador',age=7,category=cls.alfa,self_registered=True)
    def play(self,mode='solo',category=None):
        a=game.create_attempt(self.student,self.user,mode,category);game.action(a.pk,'start')
        if mode=='mission':game.action(a.pk,'goal')
        return a
    def answer(self,a,correct=True):
        a.refresh_from_db();item=a.items.get(position=a.current)
        game.action(a.pk,'answer',a.current,item.snapshot['correct'] if correct else (item.snapshot['correct']+1)%4)
        a.refresh_from_db();return item
    def master(self,category,n):
        for q in Question.objects.filter(category=category)[:n]:Mastery.objects.get_or_create(student=self.student,question=q,category=category)
    def profile(self,**kw):
        return Student.objects.create(name='Perfil escolar',age=7,category=self.alfa,teacher=self.teacher,claim_code=uuid.uuid4().hex,**kw)
    def bulk(self,**extra):
        data={'pupils-TOTAL_FORMS':'2','pupils-INITIAL_FORMS':'0','pupils-0-name':'Ana','pupils-0-age':'7','pupils-1-name':'Luis','pupils-1-age':'10','new_group':'Equipo A'}
        return self.client.post(reverse('escuela:bulk_students'),{**data,**extra})
    def test_alfa_has_no_deadline_in_both_modes(self):
        for mode in ['solo','mission']:
            a=self.play(mode);a.refresh_from_db();self.assertEqual(a.seconds,0);self.assertIsNone(a.deadline)
            with patch('core.services.game.timezone.now',return_value=timezone.now()+timedelta(days=1)):d=game.status(a.pk)
            self.assertEqual(d['current'],0);self.assertIsNone(d['deadline'])
    def test_solo_route_steps_equal_questions_and_all_correct_win(self):
        a=self.play();route=a.board['routes'][0]
        self.assertEqual(a.total_questions,len(route)-1);self.assertEqual(a.items.count(),a.total_questions)
        self.assertEqual(len(paths(set(a.board['safe']),a.board['goal'])),1)
        for _ in range(a.total_questions):self.answer(a)
        self.assertEqual(a.state,'won');self.assertEqual(a.score,a.total_questions)
    def test_solo_failure_preserves_unique_mastery_and_real_virus_path(self):
        a=self.play();first=self.answer(a);self.answer(a,False)
        self.assertEqual(a.state,'lost');self.assertEqual(a.current,2);self.assertEqual(a.score,1)
        self.assertTrue(Mastery.objects.filter(student=self.student,question=first.question).exists())
        path=a.board['crash_path'];self.assertEqual(path[0],a.board['routes'][0][1]);self.assertNotIn(path[-1],a.board['safe'])
        for x,y in zip(path,path[1:]):self.assertIn(y,neighbors(x))
        self.assertIsNone(a.deadline)
    def test_crash_path_from_every_safe_position_is_orthogonal(self):
        for code in ['ALFA','BETA','OMEGA']:
            for seed in range(10):
                b=generate(code,random.Random(seed),route_count=1)
                for p in b['safe']:
                    route=crash_path(b,p);self.assertEqual(route[0],p);self.assertNotIn(route[-1],b['safe'])
                    for x,y in zip(route,route[1:]):self.assertIn(y,neighbors(x))
    def test_beta_and_omega_timeouts_are_errors_and_end_solo(self):
        self.student.age=14;self.student.save()
        for category,seconds in [(self.beta,35),(self.omega,30)]:
            a=self.play(category=category);a.refresh_from_db();deadline=a.deadline;self.assertEqual(a.seconds,seconds)
            with patch('core.services.game.timezone.now',return_value=deadline+timedelta(seconds=1)):d=game.status(a.pk)
            self.assertEqual(d['state'],'lost');self.assertEqual(d['errors'],1);self.assertTrue(d['last_answer']['timeout'])
            game.action(a.pk,'answer',0,a.items.first().snapshot['correct']);a.refresh_from_db();self.assertEqual(a.score,0)
    def test_dynamic_immediately_advances_and_always_asks_five(self):
        a=self.play('mission')
        for i in range(5):
            self.answer(a,i<3);d=game.status(a.pk)
            self.assertEqual(d['current'],i+1);self.assertIsNone(a.next_at)
            if i<4:self.assertEqual(d['question']['position'],i+1)
        self.assertEqual(a.state,'won');self.assertEqual(a.score,3);self.assertEqual(a.total_questions,5)
    def test_95_unique_not_enough_but_96_unlock_next(self):
        self.master(self.alfa,95);self.assertFalse(can_play(self.student,self.beta))
        self.master(self.alfa,96);self.assertTrue(can_play(self.student,self.beta));self.assertFalse(can_play(self.student,self.omega))
        self.assertEqual(Mastery.objects.filter(student=self.student).count(),96)
    def test_unlock_is_sticky_after_more_questions_or_retirements(self):
        self.master(self.alfa,96);worlds(self.student)
        q=Question.objects.filter(category=self.alfa).first();q.pk=None;q.seed_key=None;q.text='Otra pregunta';q.save()
        self.assertTrue(can_play(self.student,self.beta));self.assertTrue(WorldUnlock.objects.filter(student=self.student,category=self.beta).exists())
    def test_repeat_correct_question_counts_once_across_failed_attempts(self):
        a=self.play();first=self.answer(a);self.answer(a,False)
        b=self.play();item=b.items.first();item.question=first.question;item.save()
        self.answer(b);self.answer(b,False)
        self.assertEqual(Mastery.objects.filter(student=self.student,question=first.question).count(),1)
    def test_older_students_also_unlock_previous_worlds(self):
        self.student.age=10;self.student.save();self.assertEqual([r['unlocked'] for r in worlds(self.student)],[True,True,False])
        self.student.age=12;self.student.save();self.assertTrue(all(r['unlocked'] for r in worlds(self.student)))
    def test_difficulty_progress_makes_whole_bank_reachable(self):
        self.assertEqual(learning_tier(self.student,self.alfa),1)
        for tier in [1,2]:
            for q in Question.objects.filter(category=self.alfa,difficulty=tier)[:32]:Mastery.objects.create(student=self.student,question=q,category=self.alfa)
            self.assertEqual(learning_tier(self.student,self.alfa),tier+1)
    def test_locked_world_rejected_on_server(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('juego:choose_mode',args=['OMEGA'])).status_code,403)
        self.assertEqual(self.client.post(reverse('juego:start'),{'category':'OMEGA','mode':'solo'}).status_code,403)
        self.assertFalse(Attempt.objects.exists())
    def test_student_can_control_own_dynamic_board(self):
        self.client.force_login(self.user);self.client.post(reverse('juego:start'),{'mode':'mission'})
        a=Attempt.objects.get()
        for command,expected in [('start','board'),('goal','quiz')]:
            r=self.client.post(reverse('juego:api_action',args=[a.pk]),json.dumps({'command':command}),content_type='application/json')
            self.assertEqual(r.status_code,200);self.assertEqual(r.json()['state'],expected)
    def test_bulk_profiles_and_inline_group_create_no_accounts(self):
        self.client.force_login(self.teacher);users=User.objects.count();self.assertEqual(self.bulk().status_code,302)
        self.assertEqual(User.objects.count(),users);room=Classroom.objects.get(name='Equipo A')
        self.assertEqual(room.student_set.count(),2)
        self.assertEqual(Student.objects.get(name='Luis').category,self.beta)
    def test_invalid_bulk_is_atomic_including_inline_group(self):
        self.client.force_login(self.teacher);self.assertEqual(self.bulk(**{'pupils-1-age':'2'}).status_code,200)
        self.assertFalse(Classroom.objects.filter(name='Equipo A').exists());self.assertFalse(Student.objects.filter(name='Ana').exists())
    def test_bulk_foreign_group_and_student_access_rejected(self):
        room=Classroom.objects.create(name='Otro',teacher=self.other);self.client.force_login(self.teacher)
        self.assertEqual(self.bulk(classroom=room.pk,new_group='').status_code,200)
        self.assertEqual(room.student_set.count(),0)
        self.client.force_login(self.user);self.assertEqual(self.bulk().status_code,403)
    def test_teacher_can_play_retry_and_archive_profile_without_user(self):
        s=self.profile();self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(reverse('juego:start'),{'student':s.pk,'mode':'solo'}).status_code,302)
        a=s.attempts.get();game.action(a.pk,'start');self.answer(a,False)
        self.assertEqual(self.client.get(reverse('progreso:result',args=[a.pk])).status_code,200)
        self.assertEqual(self.client.post(reverse('juego:retry',args=[a.pk])).status_code,302)
        self.client.post(reverse('escuela:student_delete',args=[s.pk]));s.refresh_from_db();self.assertFalse(s.active);self.assertEqual(s.attempts.count(),2)
    def test_claim_combines_histories_and_mastery_once(self):
        target=self.profile();oldpk=self.student.pk;code=target.claim_code
        a=self.play();first=self.answer(a);self.answer(a,False)
        b=game.create_attempt(target,self.teacher,'solo');game.action(b.pk,'start');item=self.answer(b);self.answer(b,False)
        result=claim_profile(self.user,code)
        self.assertEqual(result.pk,target.pk);self.assertEqual(result.user,self.user);self.assertIsNone(result.claim_code)
        self.assertFalse(Student.objects.filter(pk=oldpk).exists());self.assertEqual(result.attempts.count(),2)
        self.assertTrue(result.masteries.filter(question=first.question).exists());self.assertTrue(result.masteries.filter(question=item.question).exists())
        with self.assertRaises(ValidationError):claim_profile(self.user,code)
    def test_claim_cannot_cross_teachers_or_use_disabled_profile(self):
        target=self.profile();self.student.teacher=self.other;self.student.save()
        with self.assertRaises(ValidationError):claim_profile(self.user,target.claim_code)
        self.student.teacher=None;self.student.save();target.active=False;target.save()
        with self.assertRaises(ValidationError):claim_profile(self.user,target.claim_code)
        target.refresh_from_db();self.assertIsNone(target.user_id)
    def test_teacher_email_required_student_email_optional(self):
        data={'username':'fresh','first_name':'Test','role':'teacher','password1':'Test-password-2026','password2':'Test-password-2026'}
        self.assertEqual(self.client.post(reverse('cuentas:register'),data).status_code,200);self.assertFalse(User.objects.filter(username='fresh').exists())
        data.update(role='student',age=7);self.assertEqual(self.client.post(reverse('cuentas:register'),data).status_code,302)
        self.assertEqual(User.objects.get(username='fresh').email,'')
    def test_password_recovery_emits_valid_reset_link(self):
        r=self.client.post(reverse('cuentas:password_reset'),{'email':self.teacher.email});self.assertEqual(r.status_code,302);self.assertEqual(len(mail.outbox),1)
        import re
        url=re.search(r'http://testserver([^\s]+)',mail.outbox[0].body).group(1)
        r=self.client.get(url);self.assertEqual(r.status_code,302)
        r=self.client.post(r.url,{'new_password1':'New-password-2026','new_password2':'New-password-2026'})
        self.assertEqual(r.status_code,302);self.teacher.refresh_from_db();self.assertTrue(self.teacher.check_password('New-password-2026'))
    def test_resize_assets_and_new_pages_render(self):
        self.client.force_login(self.teacher);self.assertEqual(self.client.get(reverse('escuela:bulk_students')).status_code,200)
        s=self.profile();self.assertContains(self.client.get(reverse('escuela:student_detail',args=[s.pk])),s.claim_code)
        self.client.force_login(self.user)
        for name in ['escuela:claim_profile', 'cuentas:profile']:self.assertEqual(self.client.get(reverse(name)).status_code,200)
        self.assertContains(self.client.get(reverse('juego:choose_mode',args=['ALFA'])),'Individual')

class UpgradePreservationTests(TransactionTestCase):
    def test_upgrade_preserves_accounts_attempts_and_backfills_unique_progress(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        before=[('core','0002_public_registration')]
        after=[('core','0006_domain_apps')]
        executor=MigrationExecutor(connection);executor.migrate(before)
        try:
            apps=executor.loader.project_state(before).apps
            U=apps.get_model('core','User');C=apps.get_model('core','Category');S=apps.get_model('core','Student')
            subject=apps.get_model('core','Subject').objects.create(name='Matemáticas')
            cat=C.objects.create(code='ALFA',name='Laboratorio',min_age=6,max_age=8,seconds=40,routes=2)
            C.objects.create(code='BETA',name='Ciudad',min_age=9,max_age=11,seconds=35,routes=2)
            C.objects.create(code='OMEGA',name='Virus',min_age=12,max_age=14,seconds=30,routes=1)
            user=U.objects.create(username='legacy',first_name='Nombre anterior',password='preserved-hash')
            student=S.objects.create(user=user,age=7,category=cat,self_registered=True)
            q=apps.get_model('core','Question').objects.create(subject=subject,category=cat,difficulty=1,topic='Suma',text='1+1',option_a='2',option_b='3',option_c='4',option_d='5',correct=0,explanation='Dos',status='published')
            A=apps.get_model('core','Attempt');I=apps.get_model('core','AttemptQuestion')
            ids=[]
            for _ in range(2):
                a=A.objects.create(student=student,operator=user,category=cat,difficulty=1,seconds=40,mode='practice',state='lost',score=1,current=5)
                ids.append(a.pk);I.objects.create(attempt=a,question=q,position=0,snapshot={'text':'1+1','options':['2','3','4','5'],'correct':0},selected=0,correct=True,answered_at=timezone.now())
            executor=MigrationExecutor(connection);executor.migrate(after)
            s=Student.objects.get(pk=student.pk)
            self.assertEqual(s.name,'Nombre anterior');self.assertEqual(s.user.password,'preserved-hash')
            self.assertEqual(Attempt.objects.filter(pk__in=ids,state='lost',score=1,total_questions=5).count(),2)
            self.assertEqual(s.masteries.count(),1);self.assertTrue(s.world_unlocks.filter(category__code='BETA').exists())
            self.assertEqual(Category.objects.get(code='ALFA').seconds,0)
        finally:
            MigrationExecutor(connection).migrate(after)
