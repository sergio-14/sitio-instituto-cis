"""
URL configuration for administrador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from instituto import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.signout, name='logout'),
    
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/activar/<int:pk>/', views.activar_usuario, name='activar_usuario'),
    path('usuarios/deshabilitar/<int:pk>/', views.deshabilitar_usuario, name='deshabilitar_usuario'),
    
    path('docentes/', views.listar_docentes, name='listar_docentes'),
    path('docentes/agregar/', views.agregar_editar_docente, name='agregar_docente'),
    path('docentes/editar/<int:pk>/', views.agregar_editar_docente, name='editar_docente'),

    path('estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
    path('estudiantes/agregar/', views.agregar_editar_estudiante, name='agregar_estudiante'),
    path('estudiantes/editar/<int:pk>/', views.agregar_editar_estudiante, name='editar_estudiante'),
    
    
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/agregar/', views.agregar_curso, name='agregar_curso'),
    path('cursos/editar/<int:curso_id>/', views.editar_curso, name='editar_curso'),
    
    path('inscripciones/', views.lista_inscripciones, name='lista_inscripciones'),
    path('inscripciones/agregar/', views.agregar_inscripcion, name='agregar_inscripcion'),
    path('inscripciones/editar/<int:inscripcion_id>/', views.editar_inscripcion, name='editar_inscripcion'),

    # Rutas para Pagos
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pagos/agregar/', views.agregar_pago, name='agregar_pago'),
    path('pagos/editar/<int:pago_id>/', views.editar_pago, name='editar_pago'),
    
    
    path('buscar_estudiante/', views.buscar_estudiante, name='buscar_estudiante'),
    path('inscripciones_por_estudiante/', views.inscripciones_por_estudiante, name='inscripciones_por_estudiante'),
    
    
    path('lista/certificados', views.lista_certificados, name='lista_certificados'),
    path('crear/<int:inscripcion_id>/', views.crear_certificado, name='crear_certificado'),
    path('certificado/<int:certificado_id>/guardar/', views.guardar_posiciones_certificado, name='guardar_posiciones_certificado'),
    path('ver/<int:certificado_id>/', views.ver_certificado, name='ver_certificado'),
    path('editar_certificado/<int:certificado_id>/', views.editar_certificado, name='editar_certificado'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)