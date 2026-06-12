"""
Vistas del sistema de Gestión de Actividades Escolares.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
import json
import google.generativeai as genai
from django.conf import settings
from .models import (
    User, Seccion, Destino, ActividadInstitucional,
    PropuestaActividad, Excursion, Evidencia, Aviso, Mensaje
)
from .forms import (
    LoginForm, ActividadForm, PropuestaForm, RevisionPropuestaForm,
    ExcursionForm, EvidenciaForm, AvisoForm, MensajeForm, PerfilForm,
    SeccionForm, DestinoForm, RegistroDocenteForm
)
from .utils import generar_pdf_actividad, generar_pdf_reporte_general
import functools


# ─── Decoradores de rol ───────────────────────────────────────────────────────

def director_required(view_func):
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_director:
            messages.error(request, 'Acceso restringido: solo el director puede realizar esta acción.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def docente_required(view_func):
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_docente:
            messages.error(request, 'Acceso restringido: acción solo para docentes.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Autenticación ───────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido/a, {user.get_full_name() or user.username}.')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


def registro_docente(request):
    """Registro público para docentes. La cuenta queda inactiva hasta que el director la apruebe."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistroDocenteForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Cuenta creada exitosamente. El director debe aprobar tu acceso antes de que puedas ingresar.'
            )
            return redirect('login')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    return render(request, 'registro_docente.html', {'form': form})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    mensajes_no_leidos = Mensaje.objects.filter(para_usuario=user, leido=False).count()
    avisos_recientes = Aviso.objects.filter(activo=True).order_by('-fecha_creacion')[:5]

    if user.is_director:
        actividades = ActividadInstitucional.objects.all().select_related('created_by')
        propuestas_pendientes = PropuestaActividad.objects.filter(estado='pendiente')
        excursiones = Excursion.objects.all().select_related('seccion', 'destino', 'responsable')
        docentes = User.objects.filter(role='docente', is_active=True)
        docentes_pendientes = User.objects.filter(role='docente', is_active=False).count()
        stats = {
            'total_actividades': actividades.count(),
            'actividades_pendientes': actividades.filter(estado='pendiente').count(),
            'actividades_en_proceso': actividades.filter(estado='en_proceso').count(),
            'actividades_finalizadas': actividades.filter(estado='finalizada').count(),
            'propuestas_pendientes': propuestas_pendientes.count(),
            'total_excursiones': excursiones.count(),
            'total_docentes': docentes.count(),
            'docentes_pendientes': docentes_pendientes,
            'mensajes_no_leidos': mensajes_no_leidos,
        }
        ctx = {
            'actividades_recientes': actividades.order_by('-fecha_creacion')[:6],
            'propuestas_pendientes': propuestas_pendientes[:5],
            'excursiones_proximas': excursiones.filter(
                fecha__gte=timezone.now().date(), estado='programada'
            ).order_by('fecha')[:5],
            'avisos_recientes': avisos_recientes,
            'stats': stats,
        }
        return render(request, 'dashboard_director.html', ctx)
    else:
        # Docente
        mis_actividades = ActividadInstitucional.objects.filter(
            responsables=user
        ).select_related('created_by')
        mis_excursiones = Excursion.objects.filter(
            responsable=user
        ).select_related('seccion', 'destino')
        mis_propuestas = PropuestaActividad.objects.filter(propuesta_por=user)
        stats = {
            'mis_actividades': mis_actividades.count(),
            'actividades_pendientes': mis_actividades.filter(estado='pendiente').count(),
            'mis_excursiones': mis_excursiones.count(),
            'propuestas_enviadas': mis_propuestas.count(),
            'propuestas_aprobadas': mis_propuestas.filter(estado='aprobada').count(),
            'mensajes_no_leidos': mensajes_no_leidos,
        }
        ctx = {
            'mis_actividades': mis_actividades.order_by('-fecha')[:6],
            'mis_excursiones': mis_excursiones.order_by('fecha')[:5],
            'mis_propuestas': mis_propuestas[:5],
            'avisos_recientes': avisos_recientes,
            'stats': stats,
        }
        return render(request, 'dashboard_docente.html', ctx)


# ─── Actividades Institucionales ─────────────────────────────────────────────

@login_required
def actividades_lista(request):
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    user = request.user

    if user.is_director:
        qs = ActividadInstitucional.objects.all()
    else:
        qs = ActividadInstitucional.objects.filter(responsables=user)

    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))
    if estado:
        qs = qs.filter(estado=estado)

    qs = qs.select_related('created_by').prefetch_related('responsables', 'evidencias')
    return render(request, 'actividades/lista.html', {
        'actividades': qs,
        'q': q,
        'estado': estado,
        'estados': ActividadInstitucional.ESTADO_CHOICES,
    })


@director_required
def actividad_crear(request):
    form = ActividadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        actividad = form.save(commit=False)
        actividad.created_by = request.user
        actividad.save()
        messages.success(request, f'Actividad "{actividad.titulo}" creada exitosamente. Ya aparece en el calendario.')
        # Redirigir al calendario en el mes de la actividad
        return redirect(
            f"/calendario/?year={actividad.fecha.year}&month={actividad.fecha.month}"
        )
    return render(request, 'actividades/form.html', {'form': form, 'titulo': 'Nueva Actividad'})


@login_required
def actividad_detalle(request, pk):
    user = request.user
    if user.is_director:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk)
    else:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk, responsables=user)

    evidencias = actividad.evidencias.all().select_related('subido_por')
    form_evidencia = EvidenciaForm()
    return render(request, 'actividades/detalle.html', {
        'actividad': actividad,
        'evidencias': evidencias,
        'form_evidencia': form_evidencia,
    })


@director_required
def actividad_editar(request, pk):
    actividad = get_object_or_404(ActividadInstitucional, pk=pk)
    form = ActividadForm(request.POST or None, request.FILES or None, instance=actividad)
    if request.method == 'POST' and form.is_valid():
        actividad = form.save()
        messages.success(request, 'Actividad actualizada correctamente. El calendario refleja el cambio.')
        # Redirigir al calendario en el mes de la actividad
        return redirect(
            f"/calendario/?year={actividad.fecha.year}&month={actividad.fecha.month}"
        )
    return render(request, 'actividades/form.html', {
        'form': form,
        'titulo': 'Editar Actividad',
        'actividad': actividad,
    })


@director_required
def actividad_eliminar(request, pk):
    actividad = get_object_or_404(ActividadInstitucional, pk=pk)
    if request.method == 'POST':
        titulo = actividad.titulo
        actividad.delete()
        messages.success(request, f'Actividad "{titulo}" eliminada.')
        return redirect('actividades_lista')
    return render(request, 'actividades/confirmar_eliminar.html', {'actividad': actividad})


# ─── Propuestas de Actividad ─────────────────────────────────────────────────

@login_required
def propuestas_lista(request):
    user = request.user
    if user.is_director:
        qs = PropuestaActividad.objects.all()
        estado = request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)
    else:
        qs = PropuestaActividad.objects.filter(propuesta_por=user)
    qs = qs.select_related('propuesta_por', 'revisado_por')
    return render(request, 'propuestas/lista.html', {
        'propuestas': qs,
        'estado': request.GET.get('estado', ''),
    })


@docente_required
def propuesta_crear(request):
    form = PropuestaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        propuesta = form.save(commit=False)
        propuesta.propuesta_por = request.user
        propuesta.save()
        messages.success(request, 'Propuesta enviada al director exitosamente.')
        return redirect('propuestas_lista')
    return render(request, 'propuestas/form.html', {'form': form})


@login_required
def propuesta_detalle(request, pk):
    user = request.user
    if user.is_director:
        propuesta = get_object_or_404(PropuestaActividad, pk=pk)
    else:
        propuesta = get_object_or_404(PropuestaActividad, pk=pk, propuesta_por=user)
    return render(request, 'propuestas/detalle.html', {'propuesta': propuesta})


@director_required
def propuesta_revisar(request, pk):
    propuesta = get_object_or_404(PropuestaActividad, pk=pk, estado='pendiente')
    form = RevisionPropuestaForm(request.POST or None, instance=propuesta)
    if request.method == 'POST' and form.is_valid():
        revision = form.save(commit=False)
        revision.revisado_por = request.user
        revision.fecha_revision = timezone.now()
        revision.save()
        accion = 'aprobada' if revision.estado == 'aprobada' else 'rechazada'
        messages.success(request, f'Propuesta "{propuesta.titulo}" {accion} correctamente.')

        # Notificar al docente por mensaje interno
        Mensaje.objects.create(
            de_usuario=request.user,
            para_usuario=propuesta.propuesta_por,
            asunto=f'Tu propuesta fue {accion}: {propuesta.titulo}',
            mensaje=f'Tu propuesta "{propuesta.titulo}" ha sido {accion}.\n\n'
                    f'Comentario del director:\n{revision.observacion_admin or "Sin observaciones adicionales."}'
        )
        return redirect('propuestas_lista')
    return render(request, 'propuestas/revisar.html', {'form': form, 'propuesta': propuesta})


@director_required
def propuesta_eliminar(request, pk):
    """El director puede eliminar propuestas rechazadas o pendientes sin aprobar."""
    propuesta = get_object_or_404(PropuestaActividad, pk=pk)
    if propuesta.estado == 'aprobada':
        messages.error(request, 'No se pueden eliminar propuestas aprobadas.')
        return redirect('propuestas_lista')
    if request.method == 'POST':
        titulo = propuesta.titulo
        propuesta.delete()
        messages.success(request, f'Propuesta "{titulo}" eliminada correctamente.')
        return redirect('propuestas_lista')
    return render(request, 'propuestas/confirmar_eliminar.html', {'propuesta': propuesta})


# ─── Excursiones ─────────────────────────────────────────────────────────────

@login_required
def excursiones_lista(request):
    user = request.user
    if user.is_director:
        qs = Excursion.objects.all()
    else:
        qs = Excursion.objects.filter(responsable=user)
    qs = qs.select_related('seccion', 'destino', 'responsable').prefetch_related('evidencias')
    return render(request, 'excursiones/lista.html', {'excursiones': qs})


@login_required
def excursion_crear(request):
    form = ExcursionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        excursion = form.save(commit=False)
        excursion.responsable = request.user
        excursion.save()
        messages.success(request, 'Excursión registrada exitosamente.')
        return redirect('excursion_detalle', pk=excursion.pk)
    return render(request, 'excursiones/form.html', {'form': form, 'titulo': 'Nueva Excursión'})


@login_required
def excursion_detalle(request, pk):
    user = request.user
    if user.is_director:
        excursion = get_object_or_404(Excursion, pk=pk)
    else:
        excursion = get_object_or_404(Excursion, pk=pk, responsable=user)
    evidencias = excursion.evidencias.all()
    form_evidencia = EvidenciaForm()
    return render(request, 'excursiones/detalle.html', {
        'excursion': excursion,
        'evidencias': evidencias,
        'form_evidencia': form_evidencia,
    })


@login_required
def excursion_editar(request, pk):
    user = request.user
    if user.is_director:
        excursion = get_object_or_404(Excursion, pk=pk)
    else:
        excursion = get_object_or_404(Excursion, pk=pk, responsable=user)
    form = ExcursionForm(request.POST or None, request.FILES or None, instance=excursion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Excursión actualizada correctamente.')
        return redirect('excursion_detalle', pk=excursion.pk)
    return render(request, 'excursiones/form.html', {'form': form, 'titulo': 'Editar Excursión', 'excursion': excursion})


@login_required
def excursion_eliminar(request, pk):
    user = request.user
    if user.is_director:
        excursion = get_object_or_404(Excursion, pk=pk)
    else:
        excursion = get_object_or_404(Excursion, pk=pk, responsable=user)
    if request.method == 'POST':
        excursion.delete()
        messages.success(request, 'Excursión eliminada.')
        return redirect('excursiones_lista')
    return render(request, 'excursiones/confirmar_eliminar.html', {'excursion': excursion})


# ─── Evidencias ───────────────────────────────────────────────────────────────

@login_required
def evidencia_subir_actividad(request, pk):
    user = request.user
    if user.is_director:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk)
    else:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk, responsables=user)
    if request.method == 'POST':
        evidencia_instance = Evidencia(actividad=actividad, subido_por=request.user)
        form = EvidenciaForm(request.POST, request.FILES, instance=evidencia_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evidencia subida exitosamente.')
        else:
            messages.error(request, 'Error al subir la evidencia. Verifica el archivo.')
    return redirect('actividad_detalle', pk=pk)


@login_required
def evidencia_subir_excursion(request, pk):
    user = request.user
    if user.is_director:
        excursion = get_object_or_404(Excursion, pk=pk)
    else:
        excursion = get_object_or_404(Excursion, pk=pk, responsable=user)
    if request.method == 'POST':
        evidencia_instance = Evidencia(excursion=excursion, subido_por=request.user)
        form = EvidenciaForm(request.POST, request.FILES, instance=evidencia_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evidencia subida exitosamente.')
        else:
            messages.error(request, 'Error al subir la evidencia.')
    return redirect('excursion_detalle', pk=pk)


@login_required
def evidencia_eliminar(request, pk):
    evidencia = get_object_or_404(Evidencia, pk=pk, subido_por=request.user)
    actividad_pk = evidencia.actividad.pk if evidencia.actividad else None
    excursion_pk = evidencia.excursion.pk if evidencia.excursion else None
    if request.method == 'POST':
        evidencia.imagen.delete(save=False)
        evidencia.delete()
        messages.success(request, 'Evidencia eliminada.')
    if actividad_pk:
        return redirect('actividad_detalle', pk=actividad_pk)
    return redirect('excursion_detalle', pk=excursion_pk)


# ─── Avisos ───────────────────────────────────────────────────────────────────

@login_required
def avisos_lista(request):
    user = request.user
    if user.is_director:
        qs = Aviso.objects.filter(activo=True).select_related('creado_por')
    else:
        qs = Aviso.objects.filter(
            activo=True
        ).filter(
            Q(destinatarios=user) | Q(destinatarios__isnull=True)
        ).select_related('creado_por').distinct()
    return render(request, 'avisos/lista.html', {'avisos': qs})


@director_required
def aviso_crear(request):
    form = AvisoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        aviso = form.save(commit=False)
        aviso.creado_por = request.user
        aviso.save()
        form.save_m2m()
        messages.success(request, f'Aviso "{aviso.titulo}" publicado.')
        return redirect('avisos_lista')
    return render(request, 'avisos/form.html', {'form': form})


@director_required
def aviso_eliminar(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    if request.method == 'POST':
        aviso.activo = False
        aviso.save()
        messages.success(request, 'Aviso desactivado.')
    return redirect('avisos_lista')


# ─── Mensajería ───────────────────────────────────────────────────────────────

@login_required
def mensajes_bandeja(request):
    recibidos = Mensaje.objects.filter(para_usuario=request.user).select_related('de_usuario')
    enviados = Mensaje.objects.filter(de_usuario=request.user).select_related('para_usuario')
    no_leidos = recibidos.filter(leido=False).count()
    return render(request, 'mensajes/bandeja.html', {
        'recibidos': recibidos,
        'enviados': enviados,
        'no_leidos': no_leidos,
    })


@login_required
def mensaje_enviar(request):
    form = MensajeForm(request.POST or None, current_user=request.user)
    if request.method == 'POST' and form.is_valid():
        destinatarios = form.cleaned_data['destinatarios']
        asunto = form.cleaned_data['asunto']
        cuerpo = form.cleaned_data['mensaje']
        
        # Crear un mensaje para cada destinatario seleccionado
        for dep in destinatarios:
            Mensaje.objects.create(
                de_usuario=request.user,
                para_usuario=dep,
                asunto=asunto,
                mensaje=cuerpo
            )
            
        messages.success(request, f'Mensaje enviado correctamente a {destinatarios.count()} destinatario(s).')
        return redirect('mensajes_bandeja')
    return render(request, 'mensajes/enviar.html', {'form': form})


@login_required
def mensaje_leer(request, pk):
    msg = get_object_or_404(
        Mensaje,
        pk=pk
    )
    if msg.para_usuario != request.user and msg.de_usuario != request.user:
        raise Http404
    if msg.para_usuario == request.user:
        msg.marcar_leido()
    return render(request, 'mensajes/leer.html', {'mensaje': msg})


# ─── Reportes PDF ─────────────────────────────────────────────────────────────

@login_required
def reporte_actividad_pdf(request, pk):
    user = request.user
    if user.is_director:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk)
    else:
        actividad = get_object_or_404(ActividadInstitucional, pk=pk, responsables=user)
    buffer = generar_pdf_actividad(actividad)
    response = HttpResponse(buffer, content_type='application/pdf')
    nombre = actividad.titulo.replace(' ', '_')[:40]
    response['Content-Disposition'] = f'inline; filename="Actividad_{nombre}.pdf"'
    return response


@director_required
def reporte_general_pdf(request):
    estado = request.GET.get('estado', '')
    qs = ActividadInstitucional.objects.all().select_related('created_by').prefetch_related('responsables', 'evidencias')
    if estado:
        qs = qs.filter(estado=estado)
    buffer = generar_pdf_reporte_general(qs, estado)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_General_Actividades.pdf"'
    return response


@director_required
def reportes_panel(request):
    stats = {
        'total': ActividadInstitucional.objects.count(),
        'pendiente': ActividadInstitucional.objects.filter(estado='pendiente').count(),
        'en_proceso': ActividadInstitucional.objects.filter(estado='en_proceso').count(),
        'finalizada': ActividadInstitucional.objects.filter(estado='finalizada').count(),
        'cancelada': ActividadInstitucional.objects.filter(estado='cancelada').count(),
        'excursiones': Excursion.objects.count(),
        'evidencias': Evidencia.objects.count(),
        'propuestas_aprobadas': PropuestaActividad.objects.filter(estado='aprobada').count(),
    }
    actividades = ActividadInstitucional.objects.all().order_by('-fecha')
    return render(request, 'reportes/panel.html', {'stats': stats, 'actividades': actividades})


# ─── Perfil ───────────────────────────────────────────────────────────────────

@login_required
def perfil(request):
    form = PerfilForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')
    return render(request, 'perfil.html', {'form': form})


# ─── Gestión de Secciones/Destinos (Director) ────────────────────────────────

@director_required
def secciones_lista(request):
    secciones = Seccion.objects.annotate(num_excursiones=Count('excursiones'))
    form = SeccionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Sección creada.')
        return redirect('secciones_lista')
    return render(request, 'config/secciones.html', {'secciones': secciones, 'form': form})


@director_required
def destinos_lista(request):
    destinos = Destino.objects.annotate(num_excursiones=Count('excursiones'))
    form = DestinoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Destino creado.')
        return redirect('destinos_lista')
    return render(request, 'config/destinos.html', {'destinos': destinos, 'form': form})


# ─── Gestión de Usuarios (Director) ─────────────────────────────────────────

from .forms import UsuarioForm, UsuarioEditForm

@director_required
def usuarios_lista(request):
    usuarios = User.objects.all().order_by('role', 'username')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})

@director_required
def usuario_crear(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Usuario {user.username} creado exitosamente.')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@director_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioEditForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Editar Usuario', 'usuario': usuario})

@director_required
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('usuarios_lista')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado.')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/confirmar_eliminar.html', {'usuario': usuario})


@director_required
def aprobar_usuario(request, pk):
    """Vista para que el director apruebe o rechace una cuenta de docente pendiente."""
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            usuario.is_active = True
            usuario.save()
            messages.success(
                request,
                f'✅ Cuenta de {usuario.get_full_name() or usuario.username} aprobada. El docente ya puede iniciar sesión.'
            )
        elif accion == 'rechazar':
            nombre = usuario.get_full_name() or usuario.username
            usuario.delete()
            messages.warning(request, f'❌ Cuenta de {nombre} rechazada y eliminada del sistema.')
    return redirect('usuarios_lista')


# ─── Calendario de Actividades ────────────────────────────────────────────────

import json
import calendar as cal_module

@login_required
def calendario_actividades(request):
    """Vista de calendario mostrando actividades institucionales por mes."""
    from datetime import date
    user = request.user

    today = date.today()
    year  = int(request.GET.get('year',  today.year))
    month = int(request.GET.get('month', today.month))

    # Navegar entre meses
    if month < 1:
        month = 12; year -= 1
    elif month > 12:
        month = 1; year += 1

    # Todas las actividades institucionales del mes para todos los usuarios
    actividades_qs = ActividadInstitucional.objects.filter(
        fecha__year=year, fecha__month=month
    ).select_related('created_by').prefetch_related('responsables')

    # Serializar para JavaScript
    eventos = []
    for a in actividades_qs:
        eventos.append({
            'id': a.pk,
            'titulo': a.titulo,
            'fecha': a.fecha.strftime('%Y-%m-%d'),
            'estado': a.estado,
            'lugar': a.lugar or '',
            'url': '/actividades/{}/'.format(a.pk),
        })

    # Construir grilla preprocesada para el template
    raw_cal = cal_module.monthcalendar(year, month)
    grilla = []
    for week in raw_cal:
        fila = []
        for day in week:
            if day == 0:
                fila.append({'empty': True, 'day': 0, 'date_str': '', 'is_today': False, 'eventos': []})
            else:
                ds = '{:04d}-{:02d}-{:02d}'.format(year, month, day)
                is_t = (day == today.day and month == today.month and year == today.year)
                # Filtrar eventos del día para la celda
                eventos_dia = [e for e in eventos if e['fecha'] == ds]
                fila.append({
                    'empty': False, 
                    'day': day, 
                    'date_str': ds, 
                    'is_today': is_t,
                    'eventos': eventos_dia
                })
        grilla.append(fila)

    prev_month = month - 1 if month > 1 else 12
    prev_year  = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year  = year if month < 12 else year + 1

    nombre_mes = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ][month]

    return render(request, 'calendario/calendario.html', {
        'eventos_json': json.dumps(eventos, ensure_ascii=False),
        'year': year,
        'month': month,
        'nombre_mes': nombre_mes,
        'grilla': grilla,
        'today': today,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'actividades_mes': actividades_qs,
    })


@login_required
def calendario_api(request):
    """API JSON que devuelve las actividades del mes para polling AJAX del calendario."""
    from datetime import date
    user = request.user
    today = date.today()
    year  = int(request.GET.get('year',  today.year))
    month = int(request.GET.get('month', today.month))

    if month < 1:
        month = 12; year -= 1
    elif month > 12:
        month = 1; year += 1

    # Todas las actividades institucionales del mes para todos los usuarios
    actividades_qs = ActividadInstitucional.objects.filter(
        fecha__year=year, fecha__month=month
    ).select_related('created_by')

    eventos = []
    for a in actividades_qs:
        eventos.append({
            'id': a.pk,
            'titulo': a.titulo,
            'fecha': a.fecha.strftime('%Y-%m-%d'),
            'estado': a.estado,
            'lugar': a.lugar or '',
            'url': '/actividades/{}/'.format(a.pk),
        })

    return JsonResponse({
        'eventos': eventos,
        'total': len(eventos),
        'year': year,
        'month': month,
    })


@login_required
def chatbot_api(request):
    """API Endpoint para el Chatbot Gemini."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not settings.GEMINI_API_KEY:
                return JsonResponse({'reply': 'La clave de Gemini no está configurada en .env.', 'status': 'error'})

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            context = (
                f"Eres el Asistente Virtual Inteligente del sistema de Gestión Escolar del colegio 'María Auxiliadora'. "
                f"Estás hablando con {request.user.get_full_name() or request.user.username}, que tiene el rol de '{request.user.role}'. "
                f"Responde de forma concisa, educada y profesional. Ayuda con preguntas del sistema o de la escuela."
            )
            
            prompt = f"{context}\n\nUsuario: {user_message}\nAsistente:"
            response = model.generate_content(prompt)
            
            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'reply': f'Lo siento, tuve un problema interno: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)
