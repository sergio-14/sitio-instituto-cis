from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

# Unregister the original Group admin to avoid redundancy
admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'nombre', 'apellido', 'apellidoM',  'get_groups', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido', )
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nombre', 'apellido','apellidoM', 'imagen', 'dni', 'telefono')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido','apellidoM', 'is_active', 'is_staff', 'is_superuser', 'password1', 'password2', 'groups'),
        }),
    )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupo'

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            return super().response_add(request, obj, post_url_continue)
        return HttpResponseRedirect('/admin/usuarios/user/')

admin.site.register(User, CustomUserAdmin)

from .models import Curso, Docente, Estudiante, Inscripcion, TituloProfesional

admin.site.register(Curso)
admin.site.register(Docente)
admin.site.register(Estudiante) 
admin.site.register(Inscripcion)
admin.site.register(TituloProfesional)


from .models import Certificado, FondosCertificados

admin.site.register(Certificado)
admin.site.register(FondosCertificados)