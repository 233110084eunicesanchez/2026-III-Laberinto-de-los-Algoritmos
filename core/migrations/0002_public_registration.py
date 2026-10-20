from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import core.models


def populate_invitation_codes(apps, schema_editor):
    Classroom = apps.get_model('core', 'Classroom')
    seen = set()
    for room in Classroom.objects.using(schema_editor.connection.alias).all().iterator():
        code = core.models.invitation_code()
        while code in seen:
            code = core.models.invitation_code()
        seen.add(code)
        room.invite_code = code
        room.save(using=schema_editor.connection.alias, update_fields=['invite_code'])


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.AddField(model_name='classroom',name='invite_code',field=models.CharField('Código de invitación',max_length=12,null=True,editable=False)),
        migrations.RunPython(populate_invitation_codes,migrations.RunPython.noop),
        migrations.AlterField(model_name='classroom',name='invite_code',field=models.CharField('Código de invitación',max_length=12,unique=True,default=core.models.invitation_code,editable=False)),
        migrations.AddField(model_name='student',name='self_registered',field=models.BooleanField('Registro independiente',default=False,editable=False)),
        migrations.AlterField(model_name='student',name='teacher',field=models.ForeignKey(to=settings.AUTH_USER_MODEL,on_delete=django.db.models.deletion.PROTECT,related_name='students',null=True,blank=True)),
    ]
