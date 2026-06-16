#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de prueba realistas.
I.E. 1122 María Auxiliadora - Puno

Ejecutar con:
    python manage.py shell < seed_datos_prueba.py
o
    python manage.py runscript seed_datos_prueba  (si tienes django-extensions)
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_escolar.settings')
django.setup()

from core.models import (
    User, Seccion, Destino,
    ActividadInstitucional, PropuestaActividad,
    Excursion, Evidencia, Aviso, Mensaje
)
from django.db import transaction

print("=" * 60)
print("  SEMBRANDO DATOS DE PRUEBA - I.E. 1122 María Auxiliadora")
print("=" * 60)

today = date.today()

# ─────────────────────────────────────────────────────────────
# 1. OBTENER USUARIOS EXISTENTES
# ─────────────────────────────────────────────────────────────
print("\n[1/7] Cargando usuarios...")

director = User.objects.filter(role='director').first()
if not director:
    print("  ⚠  No se encontró ningún director. Verifica que el sistema tiene usuarios.")
    sys.exit(1)

docentes = list(User.objects.filter(role='docente').order_by('?')[:15])
if len(docentes) < 5:
    print("  ⚠  Se necesitan al menos 5 docentes. Agrega usuarios primero.")
    sys.exit(1)

print(f"  ✓ Director: {director.get_full_name() or director.username}")
print(f"  ✓ Docentes disponibles: {len(docentes)}")

# ─────────────────────────────────────────────────────────────
# 2. SECCIONES
# ─────────────────────────────────────────────────────────────
print("\n[2/7] Creando secciones...")

secciones_data = [
    ('1A', 'Primero',  'mañana'),
    ('2B', 'Segundo',  'mañana'),
    ('3C', 'Tercero',  'mañana'),
    ('4D', 'Cuarto',   'tarde'),
    ('5E', 'Quinto',   'tarde'),
    ('6F', 'Sexto',    'tarde'),
    ('6G', 'Sexto',    'mañana'),
    ('6H', 'Sexto',    'tarde'),
]

secciones = []
for nombre, nivel, turno in secciones_data:
    sec, created = Seccion.objects.get_or_create(
        nombre=nombre,
        defaults={'nivel': nivel, 'turno': turno}
    )
    secciones.append(sec)
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ Sección {nombre} ({nivel} - {turno}) [{tag}]")

# ─────────────────────────────────────────────────────────────
# 3. DESTINOS
# ─────────────────────────────────────────────────────────────
print("\n[3/7] Creando destinos para excursiones...")

destinos_data = [
    ('Reserva Nacional del Titicaca', 'Orilla del Lago Titicaca, Puno', 8.5),
    ('Parque Arqueológico de Sillustani', 'Sillustani, Puno', 35.0),
    ('Uros - Islas Flotantes', 'Lago Titicaca, Puno', 12.0),
    ('Centro Histórico de Puno', 'Jirón Lima, Puno', 3.0),
    ('Zoológico Carlos Ponce del Prado', 'Puno', 5.0),
    ('Museo Carlos Dreyer', 'Jr. Conde de Lemos 289, Puno', 2.0),
]

destinos = []
for nombre, ubicacion, dist in destinos_data:
    dest, created = Destino.objects.get_or_create(
        nombre=nombre,
        defaults={
            'ubicacion': ubicacion,
            'distancia_km': dist,
            'docente_referencia': docentes[0],
        }
    )
    destinos.append(dest)
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ {nombre} [{tag}]")

# ─────────────────────────────────────────────────────────────
# 4. ACTIVIDADES INSTITUCIONALES
# ─────────────────────────────────────────────────────────────
print("\n[4/7] Creando actividades institucionales...")

actividades_data = [
    {
        'titulo': 'Día de la Educación Peruana',
        'descripcion': (
            'Celebración del Día de la Educación en conmemoración a la fundación de la primera escuela '
            'pública del Perú. Se realizarán presentaciones artísticas de los alumnos, reconocimientos '
            'a docentes destacados y una feria de ciencias en el patio principal.'
        ),
        'fecha': today - timedelta(days=20),
        'estado': 'finalizada',
        'lugar': 'Patio principal de la I.E. 1122',
        'presupuesto': 850.00,
        'responsables': docentes[:4],
    },
    {
        'titulo': 'Simulacro de Sismo y Evacuación',
        'descripcion': (
            'Simulacro de evacuación ante sismo programado por el Ministerio de Educación. '
            'Participación obligatoria de todos los estudiantes y docentes. Se evaluará el tiempo '
            'de evacuación y la correcta ubicación en zonas de seguridad.'
        ),
        'fecha': today - timedelta(days=5),
        'estado': 'finalizada',
        'lugar': 'Toda la institución educativa',
        'presupuesto': None,
        'responsables': docentes[:6],
    },
    {
        'titulo': 'Feria de Ciencia y Tecnología FENCYT 2025',
        'descripcion': (
            'Feria científica donde los estudiantes presentarán proyectos de investigación en las áreas '
            'de ciencias naturales, tecnología e innovación. Los tres mejores proyectos representarán '
            'a la institución en la fase regional.'
        ),
        'fecha': today + timedelta(days=10),
        'estado': 'en_proceso',
        'lugar': 'Aulas del tercer piso y patio techado',
        'presupuesto': 1200.00,
        'responsables': docentes[2:7],
    },
    {
        'titulo': 'Campaña de Salud: Atenciones Médicas y Odontológicas',
        'descripcion': (
            'Campaña de salud gratuita para estudiantes en coordinación con el Centro de Salud Puno. '
            'Se realizarán evaluaciones médicas generales, revisión odontológica y talleres de '
            'higiene personal para todos los grados.'
        ),
        'fecha': today + timedelta(days=25),
        'estado': 'pendiente',
        'lugar': 'Sala de usos múltiples, I.E. 1122',
        'presupuesto': 300.00,
        'responsables': docentes[1:4],
    },
    {
        'titulo': 'Actuación por Aniversario de la I.E. 1122 María Auxiliadora',
        'descripcion': (
            'Gran actuación cívico-cultural por el aniversario de la institución. '
            'Se presentarán danzas folclóricas de la región Puno, coro institucional, '
            'poesías y números artísticos de cada sección. Participación de padres de familia y comunidad.'
        ),
        'fecha': today + timedelta(days=45),
        'estado': 'pendiente',
        'lugar': 'Coliseo Municipal de Puno',
        'presupuesto': 2500.00,
        'responsables': docentes[:8],
    },
    {
        'titulo': 'Taller de Orientación Vocacional - 6to Grado',
        'descripcion': (
            'Taller dirigido a los alumnos de sexto grado sobre orientación vocacional y el tránsito '
            'hacia el nivel secundario. Contará con charlas de psicólogos, ex-alumnos y representantes '
            'de instituciones de secundaria de Puno.'
        ),
        'fecha': today - timedelta(days=12),
        'estado': 'finalizada',
        'lugar': 'Auditorio de la I.E. 1122',
        'presupuesto': 150.00,
        'responsables': docentes[5:9],
    },
]

actividades_creadas = []
for data in actividades_data:
    responsables = data.pop('responsables')
    act, created = ActividadInstitucional.objects.get_or_create(
        titulo=data['titulo'],
        defaults={**data, 'created_by': director}
    )
    if created:
        act.responsables.set(responsables)
        act.save()
    actividades_creadas.append(act)
    estado = act.get_estado_display()
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ [{estado}] {act.titulo[:55]} [{tag}]")

# ─────────────────────────────────────────────────────────────
# 5. PROPUESTAS DE ACTIVIDAD (de docentes)
# ─────────────────────────────────────────────────────────────
print("\n[5/7] Creando propuestas de docentes...")

propuestas_data = [
    {
        'titulo': 'Visita pedagógica al Museo Carlos Dreyer',
        'descripcion': (
            'Propongo realizar una visita guiada al Museo Carlos Dreyer de Puno con los alumnos '
            'de 4to, 5to y 6to grado. La visita tiene como objetivo fortalecer el conocimiento '
            'sobre la historia y cultura puneña, complementando el área de Personal Social.'
        ),
        'propuesto_por': docentes[0],
        'estado': 'aprobada',
        'observacion_admin': 'Excelente propuesta. Se aprueba para el próximo mes. Coordinar con los padres de familia.',
        'fecha_actividad_propuesta': today + timedelta(days=30),
        'revisado_por': director,
        'fecha_revision': timezone.now() - timedelta(days=3),
    },
    {
        'titulo': 'Olimpiada de Matemáticas Interaulas',
        'descripcion': (
            'Organización de una olimpiada de matemáticas entre todas las secciones del mismo grado. '
            'Se realizarán en tres fases: clasificatoria por sección, semifinal por grado y final '
            'general. Los ganadores recibirán un certificado de reconocimiento.'
        ),
        'propuesto_por': docentes[2],
        'estado': 'pendiente',
        'observacion_admin': '',
        'fecha_actividad_propuesta': today + timedelta(days=60),
        'revisado_por': None,
        'fecha_revision': None,
    },
    {
        'titulo': 'Proyecto de Reciclaje y Medio Ambiente',
        'descripcion': (
            'Proyecto de sensibilización ambiental donde cada sección fabricará objetos útiles '
            'con material reciclado. Se culminará con una exposición para padres de familia y '
            'se entregará el material a instituciones benéficas de Puno.'
        ),
        'propuesto_por': docentes[4],
        'estado': 'rechazada',
        'observacion_admin': 'La propuesta es valiosa, sin embargo el presupuesto actual no permite su realización. Se revisará para el próximo trimestre.',
        'fecha_actividad_propuesta': today + timedelta(days=15),
        'revisado_por': director,
        'fecha_revision': timezone.now() - timedelta(days=7),
    },
    {
        'titulo': 'Taller de Primeros Auxilios para Docentes',
        'descripcion': (
            'Propongo un taller práctico de primeros auxilios básicos dirigido al personal docente '
            'y administrativo de la institución, dictado por personal de la Cruz Roja Peruana filial Puno. '
            'Duración estimada: 4 horas.'
        ),
        'propuesto_por': docentes[1],
        'estado': 'pendiente',
        'observacion_admin': '',
        'fecha_actividad_propuesta': today + timedelta(days=40),
        'revisado_por': None,
        'fecha_revision': None,
    },
    {
        'titulo': 'Concurso de Dibujo y Pintura "Puno en Colores"',
        'descripcion': (
            'Concurso artístico con temática regional donde los alumnos expresarán a través del '
            'dibujo y pintura las tradiciones, paisajes y festividades de Puno. Las mejores obras '
            'serán expuestas en el hall de la institución durante una semana.'
        ),
        'propuesto_por': docentes[6],
        'estado': 'aprobada',
        'observacion_admin': 'Aprobado. Coordinar con la APAFA para los premios. Fecha confirmada.',
        'fecha_actividad_propuesta': today + timedelta(days=20),
        'revisado_por': director,
        'fecha_revision': timezone.now() - timedelta(days=1),
    },
]

for p_data in propuestas_data:
    prop, created = PropuestaActividad.objects.get_or_create(
        titulo=p_data['titulo'],
        propuesta_por=p_data['propuesto_por'],
        defaults={
            'descripcion': p_data['descripcion'],
            'estado': p_data['estado'],
            'observacion_admin': p_data['observacion_admin'],
            'fecha_actividad_propuesta': p_data['fecha_actividad_propuesta'],
            'revisado_por': p_data['revisado_por'],
            'fecha_revision': p_data['fecha_revision'],
        }
    )
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ [{prop.get_estado_display()}] {prop.titulo[:55]} [{tag}]")

# ─────────────────────────────────────────────────────────────
# 6. EXCURSIONES
# ─────────────────────────────────────────────────────────────
print("\n[6/7] Creando excursiones...")

excursiones_data = [
    {
        'seccion': secciones[0],   # 1A
        'destino': destinos[4],    # Zoológico
        'fecha': today - timedelta(days=15),
        'responsable': docentes[0],
        'descripcion': 'Visita educativa al zoológico con enfoque en el área de Ciencia y Ambiente.',
        'num_estudiantes': 28,
        'estado': 'realizada',
    },
    {
        'seccion': secciones[5],   # 6F
        'destino': destinos[0],    # Titicaca
        'fecha': today - timedelta(days=8),
        'responsable': docentes[3],
        'descripcion': 'Excursión a la Reserva Nacional del Titicaca para el área de Personal Social y Ciencias.',
        'num_estudiantes': 32,
        'estado': 'realizada',
    },
    {
        'seccion': secciones[3],   # 4D
        'destino': destinos[1],    # Sillustani
        'fecha': today + timedelta(days=12),
        'responsable': docentes[5],
        'descripcion': 'Visita al Parque Arqueológico de Sillustani para conocer la cultura Colla y Tiahuanaco.',
        'num_estudiantes': 30,
        'estado': 'programada',
    },
    {
        'seccion': secciones[6],   # 6G
        'destino': destinos[2],    # Uros
        'fecha': today + timedelta(days=20),
        'responsable': docentes[7],
        'descripcion': 'Visita a las Islas Flotantes de los Uros como parte del proyecto de valoración cultural.',
        'num_estudiantes': 35,
        'estado': 'programada',
    },
    {
        'seccion': secciones[2],   # 3C
        'destino': destinos[5],    # Museo Dreyer
        'fecha': today - timedelta(days=30),
        'responsable': docentes[2],
        'descripcion': 'Visita al Museo Carlos Dreyer para complementar la unidad de Historia Regional.',
        'num_estudiantes': 25,
        'estado': 'realizada',
    },
    {
        'seccion': secciones[4],   # 5E
        'destino': destinos[3],    # Centro Histórico
        'fecha': today + timedelta(days=35),
        'responsable': docentes[9],
        'descripcion': 'Recorrido histórico por el centro de Puno: Plaza de Armas, Catedral y monumentos.',
        'num_estudiantes': 29,
        'estado': 'programada',
    },
]

excursiones_creadas = []
for e_data in excursiones_data:
    exc, created = Excursion.objects.get_or_create(
        seccion=e_data['seccion'],
        destino=e_data['destino'],
        fecha=e_data['fecha'],
        defaults={
            'responsable': e_data['responsable'],
            'descripcion': e_data['descripcion'],
            'num_estudiantes': e_data['num_estudiantes'],
            'estado': e_data['estado'],
        }
    )
    excursiones_creadas.append(exc)
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ [{exc.get_estado_display()}] {exc.seccion} → {exc.destino} [{tag}]")

# ─────────────────────────────────────────────────────────────
# 7. AVISOS Y MENSAJES
# ─────────────────────────────────────────────────────────────
print("\n[7/7] Creando avisos y mensajes internos...")

avisos_data = [
    {
        'titulo': '📋 Entrega de Registros de Evaluación - URGENTE',
        'mensaje': (
            'Se comunica a todos los docentes que el plazo máximo para la entrega de los registros '
            'de evaluación del primer bimestre es el día viernes de la presente semana. '
            'Entregar en secretaría en horario de 8:00 a.m. a 1:00 p.m.\n\n'
            'Los docentes que no cumplan con la entrega en el plazo establecido serán reportados '
            'a la UGEL Puno según normativa vigente.\n\n'
            'Att. La Dirección'
        ),
        'es_urgente': True,
        'activo': True,
    },
    {
        'titulo': '🎉 Felicitaciones por el Simulacro de Evacuación',
        'mensaje': (
            'La Dirección de la I.E. 1122 María Auxiliadora felicita a toda la comunidad educativa '
            'por la exitosa participación en el simulacro de evacuación ante sismo.\n\n'
            'Nuestra institución logró evacuar a todos los estudiantes en un tiempo de 2 minutos y '
            '45 segundos, superando el tiempo meta establecido por Defensa Civil.\n\n'
            '¡Excelente trabajo en equipo!'
        ),
        'es_urgente': False,
        'activo': True,
    },
    {
        'titulo': '📅 Reunión de Docentes - Jueves 8:00 a.m.',
        'mensaje': (
            'Se convoca a todos los docentes a una reunión de trabajo el día JUEVES a las 8:00 a.m. '
            'en el auditorio institucional.\n\nTemas a tratar:\n'
            '1. Planificación de actividades del segundo bimestre\n'
            '2. Resultados de la evaluación censal\n'
            '3. Organización de la Feria FENCYT\n'
            '4. Varios\n\n'
            'La asistencia es OBLIGATORIA. Puntualidad.'
        ),
        'es_urgente': True,
        'activo': True,
    },
    {
        'titulo': '📦 Materiales Educativos Disponibles en Secretaría',
        'mensaje': (
            'Se informa que ya están disponibles los materiales educativos del MINEDU correspondientes '
            'al segundo bimestre. Los docentes pueden recogerlos en secretaría presentando su DNI.\n\n'
            'Horario de atención: Lunes a viernes de 9:00 a.m. a 12:00 m.'
        ),
        'es_urgente': False,
        'activo': True,
    },
]

for a_data in avisos_data:
    aviso, created = Aviso.objects.get_or_create(
        titulo=a_data['titulo'],
        defaults={
            'mensaje': a_data['mensaje'],
            'creado_por': director,
            'es_urgente': a_data['es_urgente'],
            'activo': a_data['activo'],
        }
    )
    tag = "NUEVO" if created else "existente"
    urgente = "🔴 URGENTE" if aviso.es_urgente else "🟢 Normal"
    print(f"  ✓ [{urgente}] {aviso.titulo[:50]} [{tag}]")

# Mensajes internos entre docentes y director
mensajes_data = [
    {
        'de': docentes[0],
        'para': director,
        'asunto': 'Consulta sobre presupuesto - Excursión Zoológico',
        'mensaje': 'Estimado Director,\n\nMe dirijo a usted para consultar si es posible gestionar un presupuesto adicional para la excursión al zoológico que se realizó la semana pasada. Algunos padres de familia no pudieron cubrir el costo de transporte.\n\nQuedo a la espera de su respuesta.\n\nAtentamente.',
        'leido': True,
    },
    {
        'de': director,
        'para': docentes[0],
        'asunto': 'RE: Consulta sobre presupuesto - Excursión Zoológico',
        'mensaje': 'Estimad@ docente,\n\nGracias por su comunicación. Se revisará el fondo de actividades para ver la disponibilidad. Por favor, adjunte la lista de estudiantes afectados para gestionar el apoyo correspondiente.\n\nSaludos.',
        'leido': False,
    },
    {
        'de': docentes[3],
        'para': director,
        'asunto': 'Solicitud de permiso - Capacitación MINEDU',
        'mensaje': 'Señor Director,\n\nPor medio de la presente solicito permiso para el día de mañana a fin de asistir a una capacitación organizada por la UGEL Puno sobre nuevas metodologías de enseñanza.\n\nAdjunto el programa de la capacitación.\n\nAtentamente.',
        'leido': False,
    },
    {
        'de': docentes[1],
        'para': docentes[4],
        'asunto': 'Coordinación - Feria FENCYT',
        'mensaje': 'Hola colega,\n\nTe escribo para coordinar la presentación de nuestras secciones en la Feria FENCYT. Necesitamos definir los temas de los proyectos y el horario de ensayos.\n\n¿Puedes reunirte el miércoles en el recreo?\n\nSaludos!',
        'leido': True,
    },
    {
        'de': docentes[6],
        'para': director,
        'asunto': 'Informe - Concurso de Dibujo aprobado',
        'mensaje': 'Estimado Director,\n\nMuchas gracias por aprobar el Concurso de Dibujo y Pintura "Puno en Colores". Estamos muy contentos y ya comenzamos la planificación.\n\nLe haré llegar el cronograma detallado a la brevedad.\n\nAtentamente.',
        'leido': True,
    },
]

for m_data in mensajes_data:
    msg, created = Mensaje.objects.get_or_create(
        de_usuario=m_data['de'],
        para_usuario=m_data['para'],
        asunto=m_data['asunto'],
        defaults={
            'mensaje': m_data['mensaje'],
            'leido': m_data['leido'],
        }
    )
    tag = "NUEVO" if created else "existente"
    print(f"  ✓ [{m_data['de'].username}→{m_data['para'].username}] {m_data['asunto'][:45]} [{tag}]")

# ─────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  RESUMEN DE DATOS EN LA BASE DE DATOS")
print("=" * 60)
print(f"  👥 Usuarios:                {User.objects.count()}")
print(f"  🏫 Secciones:               {Seccion.objects.count()}")
print(f"  📍 Destinos:                {Destino.objects.count()}")
print(f"  📌 Actividades Inst.:       {ActividadInstitucional.objects.count()}")
print(f"     - Pendientes:            {ActividadInstitucional.objects.filter(estado='pendiente').count()}")
print(f"     - En Proceso:            {ActividadInstitucional.objects.filter(estado='en_proceso').count()}")
print(f"     - Finalizadas:           {ActividadInstitucional.objects.filter(estado='finalizada').count()}")
print(f"  📝 Propuestas Docentes:     {PropuestaActividad.objects.count()}")
print(f"     - Pendientes:            {PropuestaActividad.objects.filter(estado='pendiente').count()}")
print(f"     - Aprobadas:             {PropuestaActividad.objects.filter(estado='aprobada').count()}")
print(f"     - Rechazadas:            {PropuestaActividad.objects.filter(estado='rechazada').count()}")
print(f"  🚌 Excursiones:             {Excursion.objects.count()}")
print(f"     - Programadas:           {Excursion.objects.filter(estado='programada').count()}")
print(f"     - Realizadas:            {Excursion.objects.filter(estado='realizada').count()}")
print(f"  📣 Avisos:                  {Aviso.objects.count()}")
print(f"     - Urgentes:              {Aviso.objects.filter(es_urgente=True).count()}")
print(f"  ✉️  Mensajes:                {Mensaje.objects.count()}")
print(f"     - No leídos:             {Mensaje.objects.filter(leido=False).count()}")
print("=" * 60)
print("  ✅ ¡Datos de prueba cargados exitosamente!")
print("=" * 60)
