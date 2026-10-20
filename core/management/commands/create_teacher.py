from getpass import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from core.models import User
class Command(BaseCommand):
    help='Crea un profesor sin acceso al administrador y con contraseña privada.'
    def add_arguments(self,parser):parser.add_argument('username')
    def handle(self,*args,**options):
        username=options['username']
        if User.objects.filter(username=username).exists():raise CommandError('Ese usuario ya existe.')
        user=User(username=username,first_name=input('Nombre: ').strip())
        password=getpass('Contraseña: ')
        if password!=getpass('Repite la contraseña: '):raise CommandError('No coinciden.')
        try:validate_password(password,user)
        except ValidationError as e:raise CommandError(' '.join(e.messages))
        try:group=Group.objects.get(name='Profesor')
        except Group.DoesNotExist:raise CommandError('Ejecuta seed_initial primero.')
        user.set_password(password);user.save();user.groups.add(group)
        self.stdout.write(self.style.SUCCESS('Profesor creado.'))
