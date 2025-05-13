from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission
from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings




class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo de correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    imagen = models.ImageField(upload_to='Perfil/', null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    apellidoM = models.CharField(max_length=50, null=True, blank=True)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Carnet Identidad:')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
 
    # Añade los campos para las relaciones de grupos y permisos
    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='user_permissions')
    
    # Campos para la fecha de creación y modificación
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.apellidoM}'



# area cursos 


# Modelo de Docente (Información adicional)
class TituloProfesional(models.Model):
    tituloprof = models.CharField(max_length=50)

    def __str__(self):
        return self.tituloprof

class Docente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_docente')
    especialidad = models.CharField(max_length=150)
    titulo_profesional = models.ForeignKey(TituloProfesional, on_delete=models.SET_NULL, null=True, related_name='docentes')

    def __str__(self):
        return f"{self.titulo_profesional} {self.usuario.nombre} {self.usuario.apellido} {self.usuario.apellidoM}"


class Estudiante(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_estudiante')
    matricula = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellido} {self.usuario.apellidoM}"

# Modelo de Curso
class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    baner = models.ImageField(upload_to='baners/', null=True, blank=True)
    descripcion = models.TextField()
    nivel = models.CharField(max_length=50, choices=[('BASICO', 'Básico'), ('INTERMEDIO', 'Intermedio'), ('AVANZADO', 'Avanzado')])
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='cursos')
    duracion_horas = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    
    

    def __str__(self):
        return self.titulo

# Modelo de Inscripcion
class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=[('ACTIVO', 'Activo'), ('FINALIZADO', 'Finalizado'), ('RETIRADO', 'Retirado')],default='ACTIVO')
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def saldo(self):
        return self.precio_total - self.pagado

    def __str__(self):
        return f"{self.estudiante.usuario.nombre} - {self.curso.titulo}"


class Pago(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.monto} el {self.fecha_pago.strftime('%d/%m/%Y')}"
    


# area certificados 


def validar_porcentaje(value):
    """ Valida que un valor esté entre 0 y 100. """
    if value < 0 or value > 100:
        raise ValidationError(_('El valor debe estar entre 0 y 100.'))

FUENTES_DISPONIBLES = [
    ('Arial', 'Arial'),
    ('Times New Roman', 'Times New Roman'),
    ('Courier New', 'Courier New'),
    ('Verdana', 'Verdana'),
    ('Helvetica', 'Helvetica'),
    ('Georgia', 'Georgia'),
    ('Trebuchet MS', 'Trebuchet MS'),
    ('Impact', 'Impact'),
]

class FondosCertificados(models.Model):
    nombre_fondo = models.CharField(max_length=100, unique=True)
    imagen_fondo = models.ImageField(upload_to='fondos_certificados/')

    def __str__(self):
        return self.nombre_fondo

class Certificado(models.Model):
    inscripcion = models.OneToOneField(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='certificado'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True, editable=False)
    imagen_fondo = models.ForeignKey(
        FondosCertificados, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="certificados"
    )
    qr_code = models.ImageField(upload_to='qr_certificados/', blank=True, null=True)
    
    # Posiciones en porcentaje (0-100)
    pos_x_estudiante = models.PositiveIntegerField(default=50)
    pos_y_estudiante = models.PositiveIntegerField(default=65)
    pos_x_titulo = models.PositiveIntegerField(default=50)
    pos_y_titulo = models.PositiveIntegerField(default=70)
    pos_x_fecha = models.PositiveIntegerField(default=50)
    pos_y_fecha = models.PositiveIntegerField(default=75)
    pos_x_qr = models.PositiveIntegerField(default=90)
    pos_y_qr = models.PositiveIntegerField(default=90)
    
    # Campos para estilos
    tipografia = models.CharField(max_length=100, choices=FUENTES_DISPONIBLES, default='Arial')
    color_texto = models.CharField(max_length=7, default='#000000')  # Valor hexadecimal

    # Campos para tamaño (en píxeles, por ejemplo)
    fuente_estudiante = models.PositiveIntegerField(default=24)  # Tamaño de fuente para el nombre del estudiante
    fuente_titulo = models.PositiveIntegerField(default=18)      # Tamaño de fuente para el título del curso
    fuente_fecha = models.PositiveIntegerField(default=14)       # Tamaño de fuente para la fecha

    qr_width = models.PositiveIntegerField(default=200)  # Ancho del QR en píxeles
    qr_height = models.PositiveIntegerField(default=230)
   

    def generar_qr(self):
        url_certificado = f"{settings.SITE_URL}{reverse('ver_certificado', args=[self.id])}"
        qr = qrcode.make(url_certificado)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"qr_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Primero guarda para generar el ID
        if not self.qr_code:
            self.generar_qr()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificado: {self.inscripcion.estudiante} - {self.inscripcion.curso}"

    

