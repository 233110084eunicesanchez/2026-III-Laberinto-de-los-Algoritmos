"""Traslada estado y content types sin copiar/eliminar tablas ni permisos."""
from django.db import migrations

MOVED = {
    'subject': 'preguntas', 'category': 'preguntas', 'question': 'preguntas',
    'classroom': 'escuela', 'student': 'escuela',
    'attempt': 'juego', 'attemptquestion': 'juego',
    'mastery': 'progreso', 'worldunlock': 'progreso',
}

def transfer(apps, schema_editor, reverse=False):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db = schema_editor.connection.alias
    for model, domain in MOVED.items():
        source, target = (domain, 'core') if reverse else ('core', domain)
        old = ContentType.objects.using(db).filter(app_label=source, model=model).first()
        if old:
            if ContentType.objects.using(db).filter(app_label=target, model=model).exists():
                raise RuntimeError('Content type duplicado para '+model+'. Restaura el respaldo y revisa la migración antes de continuar.')
            # Conserva PK: los Permission y los permisos de usuarios/grupos siguen vinculados.
            old.app_label = target
            old.save(using=db, update_fields=['app_label'])

def forward(apps, schema_editor):
    transfer(apps, schema_editor)

def backward(apps, schema_editor):
    transfer(apps, schema_editor, reverse=True)

class Migration(migrations.Migration):
    dependencies = [('core', '0005_world_names'), ('progreso', '0001_domain_state')]
    operations = [
        migrations.SeparateDatabaseAndState(database_operations=[], state_operations=[
            migrations.DeleteModel(name=name) for name in [
                'Mastery', 'WorldUnlock', 'AttemptQuestion', 'Attempt',
                'Student', 'Classroom', 'Question', 'Category', 'Subject',
            ]
        ]),
        migrations.RunPython(forward, backward),
    ]
