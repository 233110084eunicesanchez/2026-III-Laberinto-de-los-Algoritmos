from django.db import migrations

def rename_worlds(apps,schema_editor):
    Category=apps.get_model('core','Category')
    for code,old,new in [('ALFA','Laboratorio Digital','Laboratorio del Código'),('BETA','Ciudad Tecnológica','Ciudad Conectada')]:
        Category.objects.filter(code=code,name=old).update(name=new)

class Migration(migrations.Migration):
    dependencies=[('core','0004_preserve_progress')]
    operations=[migrations.RunPython(rename_worlds,migrations.RunPython.noop)]
