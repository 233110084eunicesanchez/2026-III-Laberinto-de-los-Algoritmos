from django.db import migrations
import math

def forwards(apps, schema_editor):
    Category=apps.get_model('core','Category');Student=apps.get_model('core','Student')
    Item=apps.get_model('core','AttemptQuestion');Mastery=apps.get_model('core','Mastery')
    Unlock=apps.get_model('core','WorldUnlock');Question=apps.get_model('core','Question')
    Category.objects.filter(code='ALFA').update(seconds=0)
    # Las partidas Alfa ya empezadas también pasan a ser sin reloj.
    apps.get_model('core','Attempt').objects.filter(category__code='ALFA',state__in=['ready','board','quiz']).update(seconds=0,deadline=None)
    for item in Item.objects.filter(correct=True,answered_at__isnull=False).select_related('attempt').iterator():
        Mastery.objects.get_or_create(student_id=item.attempt.student_id,question_id=item.question_id,defaults={'category_id':item.attempt.category_id})
    codes=['ALFA','BETA','OMEGA'];categories={c.code:c for c in Category.objects.all()}
    for student in Student.objects.select_related('user','category').iterator():
        if not student.name and student.user_id:
            student.name=student.user.first_name or student.user.username;student.save(update_fields=['name'])
        rank=max(0 if student.age<=8 else 1 if student.age<=11 else 2,codes.index(student.category.code))
        for i,code in enumerate(codes):
            if code not in categories or i>rank:continue
            category=categories[code]
            Unlock.objects.get_or_create(student=student,category=category)
            pool=Question.objects.filter(category=category,status='published',subject__name='Matemáticas')
            total=pool.count()
            if total and Mastery.objects.filter(student=student,category=category,question__in=pool).count()>=math.ceil(total*.8):rank=max(rank,min(2,i+1))

class Migration(migrations.Migration):
    dependencies=[('core','0003_alter_student_options_attempt_total_questions_and_more')]
    operations=[migrations.RunPython(forwards,migrations.RunPython.noop)]
