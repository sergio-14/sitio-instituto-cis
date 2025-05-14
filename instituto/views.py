from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserChangeForm, UserForm, EstudianteForm, DocenteForm
from django.contrib.auth.decorators import login_required, permission_required
from .models import User, Docente, Estudiante
from django.contrib import messages

def home(request):
    cursos = Curso.objects.all()
    return render(request, 'home.html', {'cursos': cursos})


def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def lista_usuarios(request):
    query = request.GET.get('q')
    usuarios = User.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(apellidoM__icontains=query)
        )

    paginator = Paginator(usuarios, 14)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
def agregar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('lista_usuarios')
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/form_usuarios.html', {'form': form, 'titulo': 'Agregar Usuario'})

@login_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('lista_usuarios')
    else:
        form = CustomUserChangeForm(instance=usuario)
    return render(request, 'usuarios/form_usuarios.html', {'form': form, 'titulo': 'Editar Usuario'})

@login_required
def deshabilitar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.is_active = False
    usuario.save()
    messages.warning(request, "Usuario deshabilitado correctamente.")
    return redirect('lista_usuarios')

@login_required
def activar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.is_active = True
    usuario.save()
    return redirect('lista_usuarios')



#docente 
def listar_docentes(request):
    query = request.GET.get("q", "")
    docentes = Docente.objects.select_related('usuario').filter(
        Q(usuario__nombre__icontains=query) |
        Q(usuario__apellido__icontains=query) |
        Q(usuario__apellidoM__icontains=query)
    ).order_by('usuario__apellido')
    
    paginator = Paginator(docentes, 14)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    
    return render(request, "docentes/lista_docentes.html", {
        "page_obj": page_obj,
        "query": query,
    })

### Agregar/Editar Docente
def agregar_editar_docente(request, pk=None):
    docente = get_object_or_404(Docente, pk=pk) if pk else None

    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            return redirect('listar_docentes')
    else:
        form = DocenteForm(instance=docente)

    return render(request, 'docentes/form_docente.html', {
        'form': form,
        'titulo': 'Editar Docente' if pk else 'Agregar Docente'
    })

#estudiante

def listar_estudiantes(request):
    query = request.GET.get("q", "")
    estudiantes = Estudiante.objects.select_related('usuario').filter(
        Q(usuario__nombre__icontains=query) |
        Q(usuario__apellido__icontains=query) |
        Q(usuario__apellidoM__icontains=query)
    ).order_by('usuario__apellido')
    
    paginator = Paginator(estudiantes, 14)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    
    return render(request, "estudiantes/lista_estudiantes.html", {
        "page_obj": page_obj,
        "query": query,
    })


### Agregar/Editar Estudiante
def agregar_editar_estudiante(request, pk=None):
    estudiante = get_object_or_404(Estudiante, pk=pk) if pk else None

    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            return redirect('listar_estudiantes')
    else:
        form = EstudianteForm(instance=estudiante)

    return render(request, 'estudiantes/form_estudiante.html', {
        'form': form,
        'titulo': 'Editar Estudiante' if pk else 'Agregar Estudiante'
    })
    
    
# Iniciar Sesion
def iniciar_sesion(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            # Verificar si los campos están vacíos
            if form.cleaned_data.get('email') or form.cleaned_data.get('password'):
                form.first_attempt = False
            else:
                form.first_attempt = True
    else:
        form = CustomLoginForm()
    return render(request, 'IniciarSesion.html', {'form': form})


# Cerrar Sesión
def signout(request):
    logout(request)
    return redirect('home')


from .models import Curso
from .forms import CursoForm

def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/lista_cursos.html', {'cursos': cursos})



from django.http import JsonResponse
from django.db.models import Q
from .models import Estudiante

def buscar_estudiante(request):
    query = request.GET.get('q', '').strip()
    
    # Verificamos que la consulta tenga al menos 3 caracteres
    if len(query) < 3:
        return JsonResponse([])  # Si el término de búsqueda es muy corto, no retornamos resultados
    
    # Usamos "usuario" en lugar de "user" para filtrar
    estudiantes = Estudiante.objects.filter(
        usuario__nombre__icontains=query
    ) | Estudiante.objects.filter(
        usuario__apellido__icontains=query
    ) | Estudiante.objects.filter(
        usuario__apellidoM__icontains=query
    )
    
    estudiantes_data = [
        {
            'id': estudiante.id,
            'usuario': {
                'nombre': estudiante.usuario.nombre,
                'apellido': estudiante.usuario.apellido,
                'apellidoM': estudiante.usuario.apellidoM or ''  # Evita valores None
            }
        }
        for estudiante in estudiantes
    ]
    
    return JsonResponse(estudiantes_data, safe=False)

def agregar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_cursos')
    else:
        form = CursoForm()
    return render(request, 'cursos/form_curso.html', {'form': form, 'accion': 'Agregar Nuevo Curso'})

def editar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('lista_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'cursos/form_curso.html', {'form': form, 'accion': 'Editar Curso'})


from .models import Inscripcion, Pago
from .forms import InscripcionForm, PagoForm

# Vistas para Inscripción
def lista_inscripciones(request):
    cursos = Curso.objects.all()
    curso_id = request.GET.get('curso')
    estudiante_query = request.GET.get('estudiante')

    inscripciones = Inscripcion.objects.select_related('curso', 'estudiante')

    if curso_id:
        inscripciones = inscripciones.filter(curso__id=curso_id)

    if estudiante_query:
        inscripciones = inscripciones.filter(
            Q(estudiante__usuario__nombre__icontains=estudiante_query) |
            Q(estudiante__usuario__apellido__icontains=estudiante_query) |
            Q(estudiante__usuario__apellidoM__icontains=estudiante_query)
        )

    # Paginación (10 por página)
    paginator = Paginator(inscripciones, 14)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cursos': cursos,
        'page_obj': page_obj,
        'curso_id': curso_id,
        'estudiante_query': estudiante_query,
    }

    return render(request, 'inscripciones/lista_inscripciones.html', context)

def agregar_inscripcion(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_inscripciones')
    else:
        form = InscripcionForm()
    return render(request, 'inscripciones/form_inscripcion.html', {'form': form, 'accion': 'Agregar Inscripción'})

def editar_inscripcion(request, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    if request.method == 'POST':
        form = InscripcionForm(request.POST, instance=inscripcion)
        if form.is_valid():
            form.save()
            return redirect('lista_inscripciones')
    else:
        form = InscripcionForm(instance=inscripcion)
    return render(request, 'inscripciones/form_inscripcion.html', {'form': form, 'accion': 'Editar Inscripción'})

# Vistas para Pago
from django.core.paginator import Paginator


def lista_pagos(request):
    query = request.GET.get('q', '').strip()
    pagos = Pago.objects.all().order_by('-fecha_pago')

    if query:
        pagos = pagos.filter(
            Q(inscripcion__estudiante__usuario__nombre__icontains=query) |
            Q(inscripcion__estudiante__usuario__apellido__icontains=query) |
            Q(inscripcion__estudiante__usuario__apellidoM__icontains=query)
        )

    paginator = Paginator(pagos, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'pagos/lista_pagos.html', context)


def inscripciones_por_estudiante(request):
    student_id = request.GET.get('student_id')
    if student_id:
        inscripciones = Inscripcion.objects.filter(estudiante_id=student_id)
        data = [
            {
                'id': inscripcion.id,
                'display': str(inscripcion)  # Usa el __str__ del modelo (Nombre del estudiante - Título del curso)
            }
            for inscripcion in inscripciones
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def agregar_pago(request):
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            # Actualizar el monto pagado en la inscripción
            inscripcion = pago.inscripcion
            inscripcion.pagado += pago.monto
            inscripcion.save()
            return redirect('lista_inscripciones')
    else:
        form = PagoForm()
    return render(request, 'pagos/form_pago.html', {'form': form, 'accion': 'Agregar Pago'})

def editar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            return redirect('lista_pagos')
    else:
        form = PagoForm(instance=pago)
    return render(request, 'pagos/form_pago.html', {'form': form, 'accion': 'Editar Pago'})




from .models import Certificado

from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from .models import Inscripcion
from .forms import CertificadoForm

"""def generar_certificado(request, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)

    # Verifica que el estudiante haya completado el curso y pagado completamente
    if inscripcion.estado != 'FINALIZADO':
        return HttpResponse("No puedes generar un certificado para una inscripción no finalizada.")

    # Verifica si ya existe un certificado
    certificado, created = Certificado.objects.get_or_create(inscripcion=inscripcion)

    if created:
        certificado.generar_qr()
        certificado.save()

    return redirect('ver_certificado', certificado_id=certificado.id)"""
    
    
    
# ✅ LISTA DE CERTIFICADOS
def lista_certificados(request):
    certificados = Certificado.objects.all()
    return render(request, 'certificados/lista_certificados.html', {'certificados': certificados})

# ✅ CREAR CERTIFICADO (Manualmente)
def crear_certificado(request, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)

    # Verifica si ya existe un certificado para este estudiante
    if Certificado.objects.filter(inscripcion=inscripcion).exists():
        return HttpResponse("Este estudiante ya tiene un certificado.")

    if request.method == 'POST':
        form = CertificadoForm(request.POST, request.FILES)
        if form.is_valid():
            certificado = form.save(commit=False)
            certificado.inscripcion = inscripcion
            certificado.save()  # Guarda primero el objeto

            # Genera el QR (ya se hace en el método save, pero lo puedes llamar si lo prefieres)
            certificado.generar_qr()
            certificado.save()  # Guarda nuevamente para incluir el QR

            return redirect('lista_certificados')
    else:
        form = CertificadoForm()

    return render(request, 'certificados/crear_certificado.html', {'form': form, 'inscripcion': inscripcion})

# ✅ VER CERTIFICADO
def ver_certificado(request, certificado_id):
    certificado = get_object_or_404(Certificado, id=certificado_id)
    return render(request, 'certificados/ver_certificado.html', {'certificado': certificado})


def editar_certificado(request, certificado_id):
    certificado = get_object_or_404(Certificado, id=certificado_id)
    return render(request, 'certificados/editar_certificado.html', {'certificado': certificado})

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST



@require_POST
def guardar_posiciones_certificado(request, certificado_id):
    try:
        data = json.loads(request.body)
    except Exception as e:
        return HttpResponseBadRequest("JSON inválido")

    certificado = get_object_or_404(Certificado, id=certificado_id)

    # Actualizamos las posiciones
    certificado.pos_x_estudiante = data.get("pos_x_estudiante", certificado.pos_x_estudiante)
    certificado.pos_y_estudiante = data.get("pos_y_estudiante", certificado.pos_y_estudiante)
    certificado.pos_x_titulo = data.get("pos_x_titulo", certificado.pos_x_titulo)
    certificado.pos_y_titulo = data.get("pos_y_titulo", certificado.pos_y_titulo)
    certificado.pos_x_fecha = data.get("pos_x_fecha", certificado.pos_x_fecha)
    certificado.pos_y_fecha = data.get("pos_y_fecha", certificado.pos_y_fecha)
    certificado.pos_x_qr = data.get("pos_x_qr", certificado.pos_x_qr)
    certificado.pos_y_qr = data.get("pos_y_qr", certificado.pos_y_qr)

    # Actualizamos los estilos
    certificado.tipografia = data.get("tipografia", certificado.tipografia)
    certificado.color_texto = data.get("color_texto", certificado.color_texto)
    certificado.fuente_estudiante = data.get("fuente_estudiante", certificado.fuente_estudiante)
    certificado.fuente_titulo = data.get("fuente_titulo", certificado.fuente_titulo)
    certificado.fuente_fecha = data.get("fuente_fecha", certificado.fuente_fecha)

    # Actualizamos las dimensiones del QR
    certificado.qr_width = data.get("qr_width", certificado.qr_width)
    certificado.qr_height = data.get("qr_height", certificado.qr_height)

    certificado.save()

    return JsonResponse({"status": "ok"})


from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from .models import Certificado
import os
from django.contrib.staticfiles import finders
from .utils import link_callback

"""def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
    else:
        return uri
    if not os.path.isfile(path):
        raise Exception('No se encontró el archivo %s' % path)
    return path

# Vista para generar el PDF
def descargar_certificado_pdf(request, certificado_id):
    certificado = get_object_or_404(Certificado, id=certificado_id)
    template_path = "certificados/certificado_pdf.html"
    
    context = {"certificado": certificado}
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="certificado_{certificado.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    
    return response
"""
"""from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from django.conf import settings

# Ruta absoluta de la fuente
fuente_path = os.path.join(settings.BASE_DIR, "static", "fonts", "Oswald-Regular.ttf")

# Verifica que la fuente exista antes de registrarla
if os.path.exists(fuente_path):
    pdfmetrics.registerFont(TTFont("Oswald", fuente_path))
else:
    raise FileNotFoundError(f"No se encontró la fuente en {fuente_path}")

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import os

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from .models import Certificado

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from .models import Curso

def generar_certificado_pdf(request, certificado_id):
    from .models import Certificado  # Asegúrate de importar tu modelo
    certificado = Certificado.objects.get(id=certificado_id)

    # Renderiza el template con el contexto
    html_string = render_to_string('certificados/certificado_pdf.html', {'certificado': certificado})
    
    # Usar build_absolute_uri() para resolver las rutas relativas de las imágenes
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    
    # Define una hoja de estilos para forzar las dimensiones exactas (A4 landscape en píxeles)
    css = CSS(string='''
        @page { size: A4 landscape; margin: 0; }
        body { margin: 0; padding: 0; }
    ''')
    
    pdf_file = html.write_pdf(stylesheets=[css])
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{certificado_id}.pdf"'
    return response"""