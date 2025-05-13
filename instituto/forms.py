from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User , Docente, Estudiante
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.core.files import File


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

# Validaciones para inicio de sesión
class CustomLoginForm(forms.Form):
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_attempt = True

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                self.first_attempt = False
                if not User.objects.filter(email=email).exists():
                    self.add_error('email', "El correo electrónico no existe.")
                else:
                    self.add_error('password', "La contraseña es incorrecta.")
            elif not user.is_active:
                self.first_attempt = False
                raise forms.ValidationError("Esta cuenta está inactiva.")
        return cleaned_data

# Validaciones para registrar nuevo usuario
class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = User
        fields = (
            'email', 'nombre', 'apellido', 'apellidoM', 'dni', 'telefono', 'direccion',
            'imagen',
            'is_active', 'is_staff', 'is_superuser',
            'password1', 'password2', 'groups'
        )
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
            }
        labels = {
            'dni': 'Carnet de Identidad',
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
        }
        
        
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise ValidationError(_("La contraseña debe tener al menos 8 caracteres."))

        if not any(char.isupper() for char in password1):
            raise ValidationError(_("La contraseña debe contener al menos una mayúscula."))

        if password1.isdigit():
            raise ValidationError(_("La contraseña no puede consistir solo en números."))

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))

        return email

    
    def get_available_groups(self):
        return Group.objects.exclude(id__in=self.instance.groups.values_list('id', flat=True))

# Formulario para actualizar usuario
class CustomClearableFileInput(forms.ClearableFileInput):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
       
    )
   
    pass

class CustomUserChangeForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
      
    )
    
    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'apellidoM', 'imagen','dni', 'telefono', 'direccion', 'is_active', 'is_staff','is_superuser', 'groups')
        widgets = {
            'imagen': CustomClearableFileInput(),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
        }
        labels = {
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
        }
           
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'nombre', 'apellido', 'apellidoM', 'telefono', 'direccion', 'imagen']

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = '__all__'

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = '__all__'
     
from django import forms
from .models import Curso

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'duracion_horas': forms.NumberInput(attrs={'min': 1}),
            'precio': forms.NumberInput(attrs={'min': 0}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }
        
        
from .models import Inscripcion, Pago

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['estudiante', 'curso', 'precio_total']
        # Puedes agregar widgets si lo requieres

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['inscripcion', 'monto', 'descripcion']
        

from django import forms
from .models import Certificado

class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ['imagen_fondo']