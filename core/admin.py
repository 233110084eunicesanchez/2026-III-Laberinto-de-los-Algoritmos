from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User

@admin.register(User)
class AccountAdmin(UserAdmin):
    @admin.action(description='Asignar rol Profesor (sin acceso al administrador)')
    def make_teacher(self,request,queryset):
        for user in queryset.filter(is_superuser=False):
            if hasattr(user,'student'):continue
            user.groups.set([Group.objects.get(name='Profesor')]);user.is_staff=False;user.save()
    actions=[make_teacher]

admin.site.site_header='El laberinto · Administración'
admin.site.site_title='El laberinto'
admin.site.index_title='Centro de control'
