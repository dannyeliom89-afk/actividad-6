"""
Management command to seed the database with demo data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo data for I.E. 1122 María Auxiliadora'

    def handle(self, *args, **kwargs):
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        
        from core.models import (
            Seccion, Destino, ActividadInstitucional,
            PropuestaActividad, Excursion, Aviso, Mensaje
        )

        self.stdout.write(self.style.MIGRATE_HEADING('🌱 Iniciando seed de datos de prueba...'))

        # ── 1. Usuarios ──────────────────────────────────────────────────────
        director, created = User.objects.get_or_create(
            username='director',
            defaults={
                'email': 'director@ie1122.edu.pe',
                'first_name': 'Carlos',
                'last_name': 'Mamani Quispe',
                'role': 'director',
                'is_staff': True,
            }
        )
        if created:
            director.set_password('Director2024!')
            director.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Director creado'))
        else:
            self.stdout.write('  · Director ya existe')

        docentes_data = [
            ('docente1', 'Ana', 'Flores Huanca', 'ana.flores@ie1122.edu.pe'),
            ('docente2', 'Luis', 'Quispe Mamani', 'luis.quispe@ie1122.edu.pe'),
            ('docente3', 'María', 'Condori Apaza', 'maria.condori@ie1122.edu.pe'),
            ('docente4', 'José', 'Ccama Ticona', 'jose.ccama@ie1122.edu.pe'),
        ]
        docentes = []
        for username, first, last, email in docentes_data:
            doc, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': 'docente',
                }
            )
            if created:
                doc.set_password('Docente2024!')
                doc.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Docente {first} {last} creado'))
            docentes.append(doc)

        # ── 2. Secciones ─────────────────────────────────────────────────────
        secciones_data = [
            ('1° A', 'Primaria', 'mañana'),
            ('2° A', 'Primaria', 'mañana'),
            ('3° B', 'Primaria', 'tarde'),
            ('4° A', 'Primaria', 'mañana'),
            ('5° A', 'Primaria', 'mañana'),
            ('6° A', 'Primaria', 'mañana'),
        ]
        secciones = []
        for nombre, nivel, turno in secciones_data:
            s, _ = Seccion.objects.get_or_create(nombre=nombre, defaults={'nivel': nivel, 'turno': turno})
            secciones.append(s)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(secciones)} secciones creadas'))

        # ── 3. Destinos ──────────────────────────────────────────────────────
        destinos_data = [
            ('Parque Ecológico de Puno', 'Jr. Tarapacá, Puno', 'Espacio natural ideal para actividades al aire libre', 2.5),
            ('Museo Carlos Dreyer', 'Jr. Conde de Lemos 289, Puno', 'Museo con piezas arqueológicas del Lago Titicaca', 1.2),
            ('Isla de los Uros', 'Lago Titicaca, Puno', 'Islas flotantes de los Uros, patrimonio cultural', 8.0),
            ('Chullpas de Sillustani', 'Sillustani, Puno', 'Sitio arqueológico preincaico con chullpas funerarias', 34.0),
            ('Centro Histórico de Puno', 'Plaza de Armas, Puno', 'Recorrido por el centro histórico de la ciudad', 0.5),
        ]
        destinos = []
        for nombre, ubic, desc, dist in destinos_data:
            d, _ = Destino.objects.get_or_create(
                nombre=nombre,
                defaults={'ubicacion': ubic, 'distancia_km': dist}
            )
            destinos.append(d)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(destinos)} destinos creados'))

        # ── 4. Actividades Institucionales ───────────────────────────────────
        actividades_data = [
            ('Día del Logro Escolar 2024', 'Presentación de los logros académicos de los estudiantes ante la comunidad educativa.', date.today() + timedelta(days=15), 'Patio principal', 'pendiente'),
            ('Taller de Valores Institucionales', 'Taller vivencial sobre respeto, solidaridad y responsabilidad para docentes y alumnos.', date.today() - timedelta(days=5), 'Aula magna', 'finalizada'),
            ('Campaña de Salud Bucal', 'Brigada de salud para revisión y atención odontológica a estudiantes de primaria.', date.today() + timedelta(days=30), 'Enfermería', 'en_proceso'),
            ('Concurso de Danzas Folklóricas', 'Representación de danzas típicas de la región Puno por secciones.', date.today() - timedelta(days=20), 'Patio central', 'finalizada'),
            ('Simulacro de Sismo', 'Simulacro de evacuación ante sismos en coordinación con Defensa Civil.', date.today() + timedelta(days=7), 'Toda la institución', 'pendiente'),
            ('Feria Científica 2024', 'Exposición de proyectos científicos elaborados por los estudiantes de 4° a 6° grado.', date.today() + timedelta(days=45), 'Patio principal', 'en_proceso'),
        ]
        actividades = []
        for titulo, desc, fecha, lugar, estado in actividades_data:
            if not ActividadInstitucional.objects.filter(titulo=titulo).exists():
                act = ActividadInstitucional.objects.create(
                    titulo=titulo,
                    descripcion=desc,
                    fecha=fecha,
                    lugar=lugar,
                    estado=estado,
                    created_by=director,
                )
                # Asignar docentes responsables al azar
                responsables_elegidos = random.sample(docentes, k=random.randint(1, 3))
                act.responsables.set(responsables_elegidos)
                actividades.append(act)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(actividades)} actividades institucionales creadas'))

        # ── 5. Propuestas ────────────────────────────────────────────────────
        propuestas_data = [
            ('Visita al Planetario Virtual', 'Propongo llevar a los estudiantes de 5° y 6° a una visita virtual al planetario para reforzar el área de Ciencia y Tecnología.', docentes[0], 'pendiente', ''),
            ('Taller de Reciclaje Creativo', 'Actividad ambiental donde los alumnos aprenderán a hacer manualidades con materiales reciclados.', docentes[1], 'aprobada', 'Excelente propuesta, la programamos para el próximo mes. Coordinemos materiales.'),
            ('Escuela de Padres — Sesión Tecnología', 'Sesión informativa para padres de familia sobre el uso responsable de redes sociales en niños.', docentes[2], 'rechazada', 'Por el momento no contamos con el aforo disponible. Puede replantearse para el siguiente bimestre.'),
            ('Concurso de Oratoria Escolar', 'Competencia interna de oratoria para desarrollar habilidades comunicativas en alumnos de 4° a 6°.', docentes[3], 'pendiente', ''),
        ]
        for titulo, desc, propuesto_por, estado, obs in propuestas_data:
            if not PropuestaActividad.objects.filter(titulo=titulo).exists():
                PropuestaActividad.objects.create(
                    titulo=titulo,
                    descripcion=desc,
                    propuesta_por=propuesto_por,
                    estado=estado,
                    observacion_admin=obs,
                    revisado_por=director if estado != 'pendiente' else None,
                    fecha_revision=timezone.now() if estado != 'pendiente' else None,
                )
        self.stdout.write(self.style.SUCCESS('  ✓ 4 propuestas de actividad creadas'))

        # ── 6. Excursiones ───────────────────────────────────────────────────
        excursiones_data = [
            (secciones[5], destinos[2], date.today() + timedelta(days=20), docentes[0], 28, 'programada'),
            (secciones[4], destinos[3], date.today() - timedelta(days=30), docentes[1], 32, 'realizada'),
            (secciones[3], destinos[0], date.today() + timedelta(days=10), docentes[2], 25, 'programada'),
            (secciones[2], destinos[4], date.today() - timedelta(days=10), docentes[3], 30, 'realizada'),
        ]
        for sec, dest, fecha, resp, nalumnos, estado in excursiones_data:
            if not Excursion.objects.filter(seccion=sec, destino=dest, fecha=fecha).exists():
                Excursion.objects.create(
                    seccion=sec,
                    destino=dest,
                    fecha=fecha,
                    responsable=resp,
                    num_estudiantes=nalumnos,
                    estado=estado,
                    descripcion=f'Excursión educativa organizada por el docente responsable.',
                )
        self.stdout.write(self.style.SUCCESS('  ✓ 4 excursiones creadas'))

        # ── 7. Avisos ────────────────────────────────────────────────────────
        avisos_data = [
            ('Reunión de docentes este viernes', 'Se convoca a todos los docentes a la reunión de coordinación pedagógica el viernes 3 de mayo a las 3:00 PM en la sala de profesores. Asistencia obligatoria.', False),
            ('⚠️ SIMULACRO DE SISMO — Próxima semana', 'Se realizará el simulacro de evacuación el martes próximo a las 10:00 AM. Favor de coordinar con sus secciones los puntos de reunión asignados.', True),
            ('Entrega de libretas primer bimestre', 'La entrega de libretas de notas del primer bimestre será el viernes 10 de mayo de 8:00 AM a 12:00 PM. Cada docente deberá tener sus actas listas con 48 horas de anticipación.', False),
        ]
        for titulo, mensaje, urgente in avisos_data:
            if not Aviso.objects.filter(titulo=titulo).exists():
                Aviso.objects.create(
                    titulo=titulo,
                    mensaje=mensaje,
                    creado_por=director,
                    es_urgente=urgente,
                )
        self.stdout.write(self.style.SUCCESS('  ✓ 3 avisos creados'))

        # ── 8. Mensajes ──────────────────────────────────────────────────────
        mensajes_data = [
            (director, docentes[0], 'Coordinación Día del Logro', 'Ana, necesito que coordines la presentación de tu sección para el Día del Logro. Por favor envíame el listado de participantes antes del viernes.'),
            (docentes[0], director, 'RE: Coordinación Día del Logro', 'Buenos días director, con gusto. Le envío el listado esta tarde. ¿Necesita también el orden de presentación?'),
            (director, docentes[1], 'Material para Feria Científica', 'Luis, recuerda solicitar los materiales para la feria a la oficina administrativa con una semana de anticipación.'),
            (docentes[2], director, 'Consulta sobre presupuesto excursión', 'Director, quería consultar si hay posibilidad de ampliar el presupuesto para la excursión a Sillustani ya que el costo del bus ha subido.'),
        ]
        for de_u, para_u, asunto, msg in mensajes_data:
            if not Mensaje.objects.filter(asunto=asunto).exists():
                Mensaje.objects.create(
                    de_usuario=de_u,
                    para_usuario=para_u,
                    asunto=asunto,
                    mensaje=msg,
                )
        self.stdout.write(self.style.SUCCESS('  ✓ 4 mensajes creados'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write(self.style.SUCCESS('✅  Seed completado exitosamente!'))
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('  CREDENCIALES DE ACCESO:'))
        self.stdout.write(f'  👤 Director  → usuario: director    | pass: Director2024!')
        self.stdout.write(f'  👤 Docente 1 → usuario: docente1    | pass: Docente2024!')
        self.stdout.write(f'  👤 Docente 2 → usuario: docente2    | pass: Docente2024!')
        self.stdout.write(f'  👤 Docente 3 → usuario: docente3    | pass: Docente2024!')
        self.stdout.write(f'  👤 Docente 4 → usuario: docente4    | pass: Docente2024!')
        self.stdout.write('')
