from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from core.models import Category, Subject, Question
from core.services.question_bank import bank

class Command(BaseCommand):
    help='Crea roles, categorías y 360 preguntas; no crea contraseñas ni sobrescribe preguntas existentes.'
    @transaction.atomic
    def handle(self,*args,**options):
        teacher,_=Group.objects.get_or_create(name='Profesor')
        student,_=Group.objects.get_or_create(name='Alumno')
        teacher.permissions.set(Permission.objects.filter(content_type__app_label__in=['escuela','preguntas','juego']).exclude(codename='publish_question').filter(content_type__model__in=['classroom','student','question','attempt']).exclude(codename__in=['add_attempt','change_attempt','delete_attempt']))
        student.permissions.set(Permission.objects.filter(content_type__app_label__in=['escuela','preguntas','juego'],codename__in=['view_student','view_attempt']))
        subject,_=Subject.objects.get_or_create(name='Matemáticas')
        for code,name,low,high,seconds,routes in [('ALFA','Laboratorio del Código',6,8,0,2),('BETA','Ciudad Conectada',9,11,35,2),('OMEGA','Zona Virus',12,14,30,1)]:
            Category.objects.get_or_create(code=code,defaults={'name':name,'min_age':low,'max_age':high,'seconds':seconds,'routes':routes})
        count=0
        for data in bank():
            code=data.pop('category_code');opts=data.pop('options');key=data.pop('seed_key')
            data.update({f'option_{letter}':opts[i] for i,letter in enumerate('abcd')})
            _,created=Question.objects.get_or_create(seed_key=key,defaults={**data,'category':Category.objects.get(code=code),'subject':subject,'status':'published'})
            count+=created
        self.stdout.write(self.style.SUCCESS(f'Roles listos. Preguntas nuevas: {count}. Banco inicial: 360.'))
